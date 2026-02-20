/**
 * crypto-reporter.js
 *
 * Workers-compatible encryption for NetGuardian vulnerability reports.
 * Uses SubtleCrypto (Web Crypto API) - works in Cloudflare Workers
 * and modern browsers with zero external dependencies.
 *
 * Uses hybrid encryption:
 * - AES-256-GCM encrypts the report (no size limit)
 * - RSA-OAEP encrypts the AES key (safe for RSA size constraints)
 *
 * Replaces GPG-based approach from draft PR #3 which couldn't
 * run in the Cloudflare Workers runtime environment.
 */

const CryptoReporter = {

    // Encrypt a report using hybrid AES-256-GCM + RSA-OAEP
    // Solves RSA size limitation - report can be any size
    async encryptReport(reportData, jwkPublicKey) {
        if (!reportData?.data?.title || !reportData?.data?.severity) {
            return {
                success: false,
                error: 'Report must have data.title and data.severity'
            };
        }

        try {
            // Step 1: Generate a random AES-256-GCM key for this report
            const aesKey = await crypto.subtle.generateKey(
                { name: 'AES-GCM', length: 256 },
                true,
                ['encrypt', 'decrypt']
            );

            // Step 2: Encrypt the report with AES-GCM (no size limit)
            const iv = crypto.getRandomValues(new Uint8Array(12));
            const encoded = new TextEncoder().encode(JSON.stringify(reportData));
            const encryptedReport = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv },
                aesKey,
                encoded
            );

            // Step 3: Export AES key then encrypt it with RSA-OAEP
            const rawAesKey = await crypto.subtle.exportKey('raw', aesKey);
            const publicKey = await crypto.subtle.importKey(
                'jwk',
                jwkPublicKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['encrypt']
            );
            const encryptedAesKey = await crypto.subtle.encrypt(
                { name: 'RSA-OAEP' },
                publicKey,
                rawAesKey
            );

            return {
                success: true,
                encrypted_key: this.toBase64(encryptedAesKey),
                encrypted_payload: this.toBase64(encryptedReport),
                iv: this.toBase64(iv),
                encryption_method: 'AES-256-GCM + RSA-OAEP-256',
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Decrypt a received report using the org's private key
    async decryptReport(encryptedData, jwkPrivateKey) {
        try {
            // Step 1: Decrypt the AES key using RSA private key
            const privateKey = await crypto.subtle.importKey(
                'jwk',
                jwkPrivateKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['decrypt']
            );

            const rawAesKey = await crypto.subtle.decrypt(
                { name: 'RSA-OAEP' },
                privateKey,
                this.fromBase64(encryptedData.encrypted_key)
            );

            // Step 2: Import the decrypted AES key
            const aesKey = await crypto.subtle.importKey(
                'raw',
                rawAesKey,
                { name: 'AES-GCM' },
                false,
                ['decrypt']
            );

            // Step 3: Decrypt the actual report
            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv: this.fromBase64(encryptedData.iv) },
                aesKey,
                this.fromBase64(encryptedData.encrypted_payload)
            );

            return {
                success: true,
                report: JSON.parse(new TextDecoder().decode(decrypted))
            };

        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Generate a new RSA key pair for an organization
    // Upload public_key to NetGuardian, keep private_key secret
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