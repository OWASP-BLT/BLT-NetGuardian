const CryptoReporter = {

    validateJWK(jwk) {
        if (!jwk || typeof jwk !== 'object') return false;
        if (jwk.kty !== 'RSA') return false;
        if (!jwk.n || !jwk.e) return false;
        if (jwk.key_ops && !jwk.key_ops.includes('encrypt')) return false;
        return true;
    },

    async hashOrgId(org_id) {
        const encoded = new TextEncoder().encode(org_id);
        const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
        return Array.from(new Uint8Array(hashBuffer))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    },

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
            const rsaPublicKey = await crypto.subtle.importKey(
                'jwk',
                jwkPublicKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['wrapKey']
            );

            const aesKey = await crypto.subtle.generateKey(
                { name: 'AES-GCM', length: 256 },
                false, 
                ['encrypt']
            );

            const iv = crypto.getRandomValues(new Uint8Array(12));
            const orgIdHash = await this.hashOrgId(org_id);
            const additionalData = new TextEncoder().encode(orgIdHash);
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

    async decryptReport(encryptedPayload, wrappedKey, iv, orgIdHash, jwkPrivateKey) {
        try {
            const rsaPrivateKey = await crypto.subtle.importKey(
                'jwk',
                jwkPrivateKey,
                { name: 'RSA-OAEP', hash: 'SHA-256' },
                false,
                ['unwrapKey']
            );

            const aesKey = await crypto.subtle.unwrapKey(
                'raw',
                this.fromBase64(wrappedKey),
                rsaPrivateKey,
                { name: 'RSA-OAEP' },
                { name: 'AES-GCM', length: 256 },
                false,
                ['decrypt']
            );

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