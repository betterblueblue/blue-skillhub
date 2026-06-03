export declare class RateLimiter {
    private limit;
    private requestCount;
    private lastResetTime;
    private readonly maxRequestsPerMinute;
    private readonly resetIntervalMs;
    constructor(maxRequestsPerMinute?: number);
    execute<T>(fn: () => Promise<T>): Promise<T>;
    getStatus(): {
        requestCount: number;
        maxRequests: number;
        resetTime: number;
    };
}
//# sourceMappingURL=rate-limiter.d.ts.map