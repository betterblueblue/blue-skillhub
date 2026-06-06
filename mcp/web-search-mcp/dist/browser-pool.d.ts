import { Browser } from 'playwright';
export declare class BrowserPool {
    private browsers;
    private maxBrowsers;
    private browserTypes;
    private currentBrowserIndex;
    private headless;
    private lastUsedBrowserType;
    constructor();
    getBrowser(): Promise<Browser>;
    closeAll(): Promise<void>;
    getLastUsedBrowserType(): string;
}
//# sourceMappingURL=browser-pool.d.ts.map