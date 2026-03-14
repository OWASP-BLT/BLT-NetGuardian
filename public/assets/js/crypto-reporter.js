/**
 * crypto-reporter.js
 *
 * Workers-compatible encryption for NetGuardian vulnerability reports.
 * Uses SubtleCrypto (Web Crypto API) - works in Cloudflare Workers
 * and modern browsers with zero external dependencies.
 *
 * Replaces GPG-based approach from draft PR #3 which could not
 * run in the Cloudflare Workers runtime environment.
 *
 * Security fixes applied (thanks @Jayant2908):
 * - Full SHA-256 fingerprints, no truncation
 * - AES key non-extractable, wrapped with RSA-OAEP
 * - AAD binding in AES-GCM for ciphertext integrity
 * - JWK validation before use
 */

const CryptoReporter = {

    // Validate JWK public key structure before use
    // Rejects malformed keys and accidentally submitted private keys
    validateJWK(jwk) {
        if (!jwk || typeof jwk !== 'object') return false;
        if (jwk.kty !== 'RSA') return false;
        if (!jwk.n || !jwk.e) return false;
        if ('d' in jwk) return false; // reject private keys
        if (jwk.key_ops && !jwk.key_ops.includes('encrypt')) return false;
        return true;
    },

    // Hash org_id using full SHA-256
    // Never store or use plaintext org_id directly
    async hashOrgId(org_id) {
        const encoded = new TextEncoder().encode(org_id);
        const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
        return Array.from(new Uint8Array(hashBuffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    },

    // Encrypt a vulnerability report using hybrid RSA+AES encryption
    // AES key is wrapped with RSA-OAEP and never exported raw
    // AAD binding ties the ciphertext to this specific org
    async encryptReport(reportData, jwkPublicKey, org_id) {
        if (!reportData?.data?.title || !reportData?.data?.severity) {
            return {
                success: false,
                error: 'Report must have data.title and data.severity'
            };
        }

        if (!this.validateJWK(jwkPublicKey)) {
            return {
                success: false,
                error: 'Invalid or malformed JWK public key'
            };
        }

        try {
            // Import RSA public key for key wrapping only
            const rsaPublicKey = await crypto.subtle.importKey(
                'jwk',
                jwkPublicKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['wrapKey']
            );

            // Generate AES-GCM key
            // extractable: false means the raw key bytes can never be accessed
            const aesKey = await crypto.subtle.generateKey(
                { name: 'AES-GCM', length: 256 },
                false,
                ['encrypt']
            );

            // Random IV for AES-GCM
            const iv = crypto.getRandomValues(new Uint8Array(12));

            // Hash org_id for AAD - binds ciphertext to this org
            // Decryption will fail if AAD doesn't match
            const orgIdHash = await this.hashOrgId(org_id);
            const additionalData = new TextEncoder().encode(orgIdHash);

            // Encrypt report with AES-GCM + AAD binding
            const encoded = new TextEncoder().encode(JSON.stringify(reportData));
            const encryptedData = await crypto.subtle.encrypt(
                {
                    name: 'AES-GCM',
                    iv: iv,
                    additionalData: additionalData
                },
                aesKey,
                encoded
            );

            // Wrap AES key with RSA-OAEP instead of exporting raw bytes
            const wrappedAesKey = await crypto.subtle.wrapKey(
                'raw',
                aesKey,
                rsaPublicKey,
                { name: 'RSA-OAEP' }
            );

            return {
                success: true,
                encrypted_payload: this.toBase64(encryptedData),
                wrapped_key: this.toBase64(wrappedAesKey),
                iv: this.toBase64(iv),
                org_id_hash: orgIdHash,
                encryption_method: 'AES-GCM-256 + RSA-OAEP wrapped key',
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Decrypt a received report using org's RSA private key
    // AAD validation ensures ciphertext was meant for this org
    async decryptReport(encryptedPayload, wrappedKey, iv, orgIdHash, jwkPrivateKey) {
        try {
            const rsaPrivateKey = await crypto.subtle.importKey(
                'jwk',
                jwkPrivateKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['unwrapKey']
            );

            // Unwrap AES key using RSA private key
            const aesKey = await crypto.subtle.unwrapKey(
                'raw',
                this.fromBase64(wrappedKey),
                rsaPrivateKey,
                { name: 'RSA-OAEP' },
                { name: 'AES-GCM', length: 256 },
                false,
                ['decrypt']
            );

            // Reconstruct AAD for validation
            // Decryption fails automatically if org_id_hash doesn't match
            const additionalData = new TextEncoder().encode(orgIdHash);

            const decrypted = await crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: this.fromBase64(iv),
                    additionalData: additionalData
                },
                aesKey,
                this.fromBase64(encryptedPayload)
            );

            return {
                success: true,
                report: JSON.parse(new TextDecoder().decode(decrypted))
            };

        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Generate RSA-4096 key pair for an organization
    // Org uploads public_key to NetGuardian, keeps private_key secret
    async generateOrgKeyPair() {
        const keyPair = await crypto.subtle.generateKey(
            {
                name: 'RSA-OAEP',
                modulusLength: 4096,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: 'SHA-256'
            },
            true,
            ['wrapKey', 'unwrapKey']
        );

        return {
            public_key: await crypto.subtle.exportKey('jwk', keyPair.publicKey),
            private_key: await crypto.subtle.exportKey('jwk', keyPair.privateKey)
        };
    },

    // Full SHA-256 fingerprint of a public key - no truncation
    // Used to verify key identity without exposing the full key
    async getKeyFingerprint(jwkPublicKey) {
        const encoded = new TextEncoder().encode(JSON.stringify(jwkPublicKey));
        const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
        return Array.from(new Uint8Array(hashBuffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    },

    toBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        bytes.forEach(b => binary += String.fromCharCode(b));
        return btoa(binary);
    },

    fromBase64(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }
};

if (typeof module !== 'undefined') module.exports = CryptoReporter;