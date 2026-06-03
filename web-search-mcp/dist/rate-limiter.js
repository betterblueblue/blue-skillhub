import pLimit from 'p-limit';
export class RateLimiter {
    limit;
    requestCount = 0;
    lastResetTime = Date.now();
    maxRequestsPerMinute;
    resetIntervalMs = 60000; // 1 minute
    constructor(maxRequestsPerMinute = 10) {
        this.maxRequestsPerMinute = maxRequestsPerMinute;
        this.limit = pLimit(5); // Max 5 concurrent requests
    }
    async execute(fn) {
        // Check if we need to reset the counter
        const now = Date.now();
        if (now - this.lastResetTime >= this.resetIntervalMs) {
            this.requestCount = 0;
            this.lastResetTime = now;
        }
        // Check rate limit
        if (this.requestCount >= this.maxRequestsPerMinute) {
            const waitTime = this.resetIntervalMs - (now - this.lastResetTime);
            throw new Error(`Rate limit exceeded. Please wait ${Math.ceil(waitTime / 1000)} seconds.`);
        }
        // Execute with concurrency limit
        const result = await this.limit(async () => {
            this.requestCount++;
            return await fn();
        });
        return result;
    }
    getStatus() {
        return {
            requestCount: this.requestCount,
            maxRequests: this.maxRequestsPerMinute,
            resetTime: this.lastResetTime + this.resetIntervalMs,
        };
    }
}
//# sourceMappingURL=rate-limiter.js.map