import { SearchOptions, SearchResultWithMetadata } from './types.js';
export declare class SearchEngine {
    private readonly rateLimiter;
    private browserPool;
    constructor();
    search(options: SearchOptions): Promise<SearchResultWithMetadata>;
    private tryBrowserBraveSearch;
    private tryBrowserBraveSearchInternal;
    private tryBrowserBingSearch;
    private tryBrowserBingSearchInternal;
    private tryEnhancedBingSearch;
    private tryDirectBingSearch;
    private generateConversationId;
    private tryDuckDuckGoSearch;
    private parseSearchResults;
    private parseBraveResults;
    private parseBingResults;
    private parseDuckDuckGoResults;
    private isValidSearchUrl;
    private cleanGoogleUrl;
    private cleanBraveUrl;
    private cleanBingUrl;
    private cleanDuckDuckGoUrl;
    private assessResultQuality;
    private validateBrowserHealth;
    private handleBrowserError;
    closeAll(): Promise<void>;
}
//# sourceMappingURL=search-engine.d.ts.map