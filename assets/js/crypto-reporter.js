/**
 * crypto-reporter.js
 *
 * Workers-compatible encryption for NetGuardian vulnerability reports.
 * Uses SubtleCrypto (Web Crypto API) - works in Cloudflare Workers
 * and modern browsers with zero external dependencies.
 *
 * Replaces GPG-based approach from draft PR #3 which couldn't
 * run in the Cloudflare Workers runtime environment.
 */

const CryptoReporter = {

    // Encrypt a report with the org's RSA public key (JWK format)
    async encryptReport(reportData, jwkPublicKey) {
        if (!reportData?.data?.title || !reportData?.data?.severity) {
            return {
                success: false,
                error: 'Report must have data.title and data.severity'
            };
        }

        try {
            const publicKey = await crypto.subtle.importKey(
                'jwk',
                jwkPublicKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['encrypt']
            );

            const encoded = new TextEncoder().encode(JSON.stringify(reportData));
            const encrypted = await crypto.subtle.encrypt(
                { name: 'RSA-OAEP' },
                publicKey,
                encoded
            );

            return {
                success: true,
                encrypted_payload: this.toBase64(encrypted),
                encryption_method: 'RSA-OAEP-256',
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Generate a new RSA key pair for an organization
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
            ['encrypt', 'decrypt']
        );

        return {
            public_key: await crypto.subtle.exportKey('jwk', keyPair.publicKey),
            private_key: await crypto.subtle.exportKey('jwk', keyPair.privateKey)
        };
    },

    // Decrypt a received report using the org's private key
    async decryptReport(encryptedBase64, jwkPrivateKey) {
        try {
            const privateKey = await crypto.subtle.importKey(
                'jwk',
                jwkPrivateKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['decrypt']
            );

            const decrypted = await crypto.subtle.decrypt(
                { name: 'RSA-OAEP' },
                privateKey,
                this.fromBase64(encryptedBase64)
            );

            return {
                success: true,
                report: JSON.parse(new TextDecoder().decode(decrypted))
            };

        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Get SHA-256 fingerprint of a public key for verification
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