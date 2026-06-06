import axios from 'axios';
import * as cheerio from 'cheerio';
import { generateTimestamp, sanitizeQuery } from './utils.js';
import { RateLimiter } from './rate-limiter.js';
import { BrowserPool } from './browser-pool.js';
export class SearchEngine {
    rateLimiter;
    browserPool;
    constructor() {
        this.rateLimiter = new RateLimiter(10); // 10 requests per minute
        this.browserPool = new BrowserPool();
    }
    async search(options) {
        const { query, numResults = 5, timeout = 10000 } = options;
        const sanitizedQuery = sanitizeQuery(query);
        console.log(`[SearchEngine] Starting search for query: "${sanitizedQuery}"`);
        try {
            return await this.rateLimiter.execute(async () => {
                console.log(`[SearchEngine] Starting search with multiple engines...`);
                // Configuration from environment variables
                const enableQualityCheck = process.env.ENABLE_RELEVANCE_CHECKING !== 'false';
                const qualityThreshold = parseFloat(process.env.RELEVANCE_THRESHOLD || '0.3');
                const forceMultiEngine = process.env.FORCE_MULTI_ENGINE_SEARCH === 'true';
                const debugBrowsers = process.env.DEBUG_BROWSER_LIFECYCLE === 'true';
                console.log(`[SearchEngine] Quality checking: ${enableQualityCheck}, threshold: ${qualityThreshold}, multi-engine: ${forceMultiEngine}, debug: ${debugBrowsers}`);
                // Try multiple approaches to get search results, starting with most reliable
                const approaches = [
                    { method: this.tryBrowserGoogleSearch.bind(this), name: 'Browser Google' },
                    { method: this.tryBrowserBingSearch.bind(this), name: 'Browser Bing' },
                    { method: this.tryBrowserBraveSearch.bind(this), name: 'Browser Brave' },
                    { method: this.tryDuckDuckGoSearch.bind(this), name: 'Axios DuckDuckGo' }
                ];
                let bestResults = [];
                let bestEngine = 'None';
                let bestQuality = 0;
                for (let i = 0; i < approaches.length; i++) {
                    const approach = approaches[i];
                    try {
                        console.log(`[SearchEngine] Attempting ${approach.name} (${i + 1}/${approaches.length})...`);
                        // Use more aggressive timeouts for faster fallback
                        const approachTimeout = Math.min(timeout / 3, 4000); // Max 4 seconds per approach for faster fallback
                        const results = await approach.method(sanitizedQuery, numResults, approachTimeout);
                        if (results.length > 0) {
                            console.log(`[SearchEngine] Found ${results.length} results with ${approach.name}`);
                            // Validate result quality to detect irrelevant results
                            const qualityScore = enableQualityCheck ? this.assessResultQuality(results, sanitizedQuery) : 1.0;
                            console.log(`[SearchEngine] ${approach.name} quality score: ${qualityScore.toFixed(2)}/1.0`);
                            // Track the best results so far
                            if (qualityScore > bestQuality) {
                                bestResults = results;
                                bestEngine = approach.name;
                                bestQuality = qualityScore;
                            }
                            // If quality is excellent, return immediately (unless forcing multi-engine)
                            if (qualityScore >= 0.8 && !forceMultiEngine) {
                                console.log(`[SearchEngine] Excellent quality results from ${approach.name}, returning immediately`);
                                return { results, engine: approach.name };
                            }
                            // If quality is acceptable and this isn't Bing (first engine), return
                            if (qualityScore >= qualityThreshold && approach.name !== 'Browser Bing' && !forceMultiEngine) {
                                console.log(`[SearchEngine] Good quality results from ${approach.name}, using as primary`);
                                return { results, engine: approach.name };
                            }
                            // If this is the last engine or quality is acceptable, prepare to return
                            if (i === approaches.length - 1) {
                                if (bestQuality >= qualityThreshold || !enableQualityCheck) {
                                    console.log(`[SearchEngine] Using best results from ${bestEngine} (quality: ${bestQuality.toFixed(2)})`);
                                    return { results: bestResults, engine: bestEngine };
                                }
                                else if (bestResults.length > 0) {
                                    console.log(`[SearchEngine] Warning: Low quality results from all engines, using best available from ${bestEngine}`);
                                    return { results: bestResults, engine: bestEngine };
                                }
                            }
                            else {
                                console.log(`[SearchEngine] ${approach.name} results quality: ${qualityScore.toFixed(2)}, continuing to try other engines...`);
                            }
                        }
                    }
                    catch (error) {
                        console.error(`[SearchEngine] ${approach.name} approach failed:`, error);
                        // Handle browser-specific errors (no cleanup needed since each engine uses dedicated browsers)
                        await this.handleBrowserError(error, approach.name);
                    }
                }
                // If we have best results from earlier engines, return them
                if (bestResults.length > 0) {
                    console.log(`[SearchEngine] Using best results from ${bestEngine} (quality: ${bestQuality.toFixed(2)})`);
                    return { results: bestResults, engine: bestEngine };
                }
                console.log(`[SearchEngine] All approaches failed, returning empty results`);
                return { results: [], engine: 'None' };
            });
        }
        catch (error) {
            console.error('[SearchEngine] Search error:', error);
            if (axios.isAxiosError(error)) {
                console.error('[SearchEngine] Axios error details:', {
                    status: error.response?.status,
                    statusText: error.response?.statusText,
                    data: error.response?.data?.substring(0, 500),
                });
            }
            throw new Error(`Failed to perform search: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    async tryBrowserBraveSearch(query, numResults, timeout) {
        console.log(`[SearchEngine] Trying browser-based Brave search with dedicated browser...`);
        // Try with retry mechanism
        for (let attempt = 1; attempt <= 2; attempt++) {
            let browser;
            try {
                // Create a dedicated browser instance for Brave search only
                // Use chromium instead of firefox since firefox may not be installed
                const { chromium } = await import('playwright');
                const _proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || process.env.http_proxy;
                browser = await chromium.launch({
                    headless: process.env.BROWSER_HEADLESS !== 'false',
                    proxy: _proxy ? { server: _proxy } : undefined,
                    args: [
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ],
                });
                console.log(`[SearchEngine] Brave search attempt ${attempt}/2 with fresh browser`);
                const results = await this.tryBrowserBraveSearchInternal(browser, query, numResults, timeout);
                return results;
            }
            catch (error) {
                console.error(`[SearchEngine] Brave search attempt ${attempt}/2 failed:`, error);
                if (attempt === 2) {
                    throw error; // Re-throw on final attempt
                }
                // Small delay before retry
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            finally {
                // Always close the dedicated browser
                if (browser) {
                    try {
                        await browser.close();
                    }
                    catch (closeError) {
                        console.log(`[SearchEngine] Error closing Brave browser:`, closeError);
                    }
                }
            }
        }
        throw new Error('All Brave search attempts failed');
    }
    async tryBrowserBraveSearchInternal(browser, query, numResults, timeout) {
        // Validate browser is still functional before proceeding
        if (!browser.isConnected()) {
            throw new Error('Browser is not connected');
        }
        try {
            const context = await browser.newContext({
                userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                viewport: { width: 1366, height: 768 },
                locale: 'en-US',
                timezoneId: 'America/New_York',
            });
            try {
                const page = await context.newPage();
                // Navigate to Brave search
                const searchUrl = `https://search.brave.com/search?q=${encodeURIComponent(query)}&source=web`;
                console.log(`[SearchEngine] Browser navigating to Brave: ${searchUrl}`);
                await page.goto(searchUrl, {
                    waitUntil: 'domcontentloaded',
                    timeout: timeout
                });
                // Wait for search results to load
                try {
                    await page.waitForSelector('[data-type="web"]', { timeout: 3000 });
                }
                catch {
                    console.log(`[SearchEngine] Browser Brave results selector not found, proceeding anyway`);
                }
                // Get the page content
                const html = await page.content();
                console.log(`[SearchEngine] Browser Brave got HTML with length: ${html.length}`);
                const results = this.parseBraveResults(html, numResults);
                console.log(`[SearchEngine] Browser Brave parsed ${results.length} results`);
                await context.close();
                return results;
            }
            catch (error) {
                // Ensure context is closed even on error
                await context.close();
                throw error;
            }
        }
        catch (error) {
            console.error(`[SearchEngine] Browser Brave search failed:`, error);
            throw error;
        }
    }
    async tryBrowserGoogleSearch(query, numResults, timeout) {
        console.log(`[SearchEngine] GOOGLE: Starting browser-based search for query: "${query}"`);
        for (let attempt = 1; attempt <= 2; attempt++) {
            let browser;
            try {
                console.log(`[SearchEngine] GOOGLE: Attempt ${attempt}/2 - Launching Chromium browser...`);
                const { chromium } = await import('playwright');
                const _proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || process.env.http_proxy;
                browser = await chromium.launch({
                    headless: process.env.BROWSER_HEADLESS !== 'false',
                    proxy: _proxy ? { server: _proxy } : undefined,
                    args: [
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                    ],
                });
                console.log(`[SearchEngine] GOOGLE: Browser launched, connected: ${browser.isConnected()}`);
                const results = await this.tryBrowserGoogleSearchInternal(browser, query, numResults, timeout);
                console.log(`[SearchEngine] GOOGLE: Search completed with ${results.length} results`);
                return results;
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                console.error(`[SearchEngine] GOOGLE: Attempt ${attempt}/2 FAILED: ${errorMessage}`);
                if (attempt === 2) {
                    console.error(`[SearchEngine] GOOGLE: All attempts exhausted`);
                    throw error;
                }
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            finally {
                if (browser) {
                    try { await browser.close(); } catch (e) { /* ignore */ }
                }
            }
        }
        throw new Error('All Google search attempts failed');
    }
    async tryBrowserGoogleSearchInternal(browser, query, numResults, timeout) {
        if (!browser.isConnected()) {
            throw new Error('Browser is not connected');
        }
        try {
            const context = await browser.newContext({
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                viewport: { width: 1366, height: 768 },
                locale: 'zh-CN',
                timezoneId: 'Asia/Shanghai',
                colorScheme: 'light',
                extraHTTPHeaders: {
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }
            });
            try {
                const page = await context.newPage();
                const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&num=${numResults}&hl=zh-CN`;
                console.log(`[SearchEngine] GOOGLE: Navigating to ${searchUrl}`);
                await page.goto(searchUrl, {
                    waitUntil: 'domcontentloaded',
                    timeout: timeout
                });
                // Wait for results to appear
                try {
                    await page.waitForSelector('#search, .g', { timeout: 5000 });
                }
                catch {
                    console.log(`[SearchEngine] GOOGLE: Results selector not found, proceeding anyway`);
                }
                const html = await page.content();
                console.log(`[SearchEngine] GOOGLE: Got HTML with length: ${html.length}`);
                const results = this.parseGoogleResults(html, numResults);
                console.log(`[SearchEngine] GOOGLE: Parsed ${results.length} results`);
                await context.close();
                return results;
            }
            catch (error) {
                await context.close();
                throw error;
            }
        }
        catch (error) {
            console.error(`[SearchEngine] GOOGLE: Search failed:`, error);
            throw error;
        }
    }
    async tryBrowserBingSearch(query, numResults, timeout) {
        const debugBing = process.env.DEBUG_BING_SEARCH === 'true';
        console.error(`[SearchEngine] BING: Starting browser-based search with dedicated browser for query: "${query}"`);
        // Try with retry mechanism
        for (let attempt = 1; attempt <= 2; attempt++) {
            let browser;
            try {
                console.error(`[SearchEngine] BING: Attempt ${attempt}/2 - Launching Chromium browser...`);
                // Create a dedicated browser instance for Bing search only
                const { chromium } = await import('playwright');
                const startTime = Date.now();
                const _proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || process.env.https_proxy || process.env.http_proxy;
                browser = await chromium.launch({
                    headless: process.env.BROWSER_HEADLESS !== 'false',
                    proxy: _proxy ? { server: _proxy } : undefined,
                    args: [
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                    ],
                });
                const launchTime = Date.now() - startTime;
                console.error(`[SearchEngine] BING: Browser launched successfully in ${launchTime}ms, connected: ${browser.isConnected()}`);
                const results = await this.tryBrowserBingSearchInternal(browser, query, numResults, timeout);
                console.error(`[SearchEngine] BING: Search completed successfully with ${results.length} results`);
                return results;
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                console.error(`[SearchEngine] BING: Attempt ${attempt}/2 FAILED with error: ${errorMessage}`);
                if (debugBing) {
                    console.error(`[SearchEngine] BING: Full error details:`, error);
                }
                if (attempt === 2) {
                    console.error(`[SearchEngine] BING: All attempts exhausted, giving up`);
                    throw error; // Re-throw on final attempt
                }
                // Small delay before retry
                console.error(`[SearchEngine] BING: Waiting 500ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            finally {
                // Always close the dedicated browser
                if (browser) {
                    try {
                        await browser.close();
                        if (debugBing) {
                            console.error(`[SearchEngine] BING: Browser closed successfully`);
                        }
                    }
                    catch (closeError) {
                        console.error(`[SearchEngine] BING: Error closing browser:`, closeError);
                    }
                }
            }
        }
        throw new Error('All Bing search attempts failed');
    }
    async tryBrowserBingSearchInternal(browser, query, numResults, timeout) {
        const debugBing = process.env.DEBUG_BING_SEARCH === 'true';
        // Validate browser is still functional before proceeding
        if (!browser.isConnected()) {
            console.error(`[SearchEngine] BING: Browser is not connected`);
            throw new Error('Browser is not connected');
        }
        console.error(`[SearchEngine] BING: Creating browser context with enhanced fingerprinting...`);
        try {
            // Enhanced browser context with more realistic fingerprinting
            const context = await browser.newContext({
                userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                viewport: { width: 1366, height: 768 },
                locale: 'en-US',
                timezoneId: 'America/New_York',
                colorScheme: 'light',
                deviceScaleFactor: 1,
                hasTouch: false,
                isMobile: false,
                extraHTTPHeaders: {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            });
            console.error(`[SearchEngine] BING: Context created, opening new page...`);
            const page = await context.newPage();
            console.error(`[SearchEngine] BING: Page opened successfully`);
            try {
                // Try enhanced Bing search with proper web interface flow
                try {
                    console.error(`[SearchEngine] BING: Attempting enhanced search (homepage → form submission)...`);
                    const results = await this.tryEnhancedBingSearch(page, query, numResults, timeout);
                    console.error(`[SearchEngine] BING: Enhanced search succeeded with ${results.length} results`);
                    await context.close();
                    return results;
                }
                catch (enhancedError) {
                    const errorMessage = enhancedError instanceof Error ? enhancedError.message : 'Unknown error';
                    console.error(`[SearchEngine] BING: Enhanced search failed: ${errorMessage}`);
                    if (debugBing) {
                        console.error(`[SearchEngine] BING: Enhanced search error details:`, enhancedError);
                    }
                    console.error(`[SearchEngine] BING: Falling back to direct URL search...`);
                    // Fallback to direct URL approach with enhanced parameters
                    const results = await this.tryDirectBingSearch(page, query, numResults, timeout);
                    console.error(`[SearchEngine] BING: Direct search succeeded with ${results.length} results`);
                    await context.close();
                    return results;
                }
            }
            catch (error) {
                // Ensure context is closed even on error
                console.error(`[SearchEngine] BING: All search methods failed, closing context...`);
                await context.close();
                throw error;
            }
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            console.error(`[SearchEngine] BING: Internal search failed: ${errorMessage}`);
            if (debugBing) {
                console.error(`[SearchEngine] BING: Internal search error details:`, error);
            }
            throw error;
        }
    }
    async tryEnhancedBingSearch(page, query, numResults, timeout) {
        const debugBing = process.env.DEBUG_BING_SEARCH === 'true';
        console.error(`[SearchEngine] BING: Enhanced search - navigating to Bing homepage...`);
        // Navigate to Bing homepage first to establish proper session
        const startTime = Date.now();
        await page.goto('https://www.bing.com', {
            waitUntil: 'domcontentloaded',
            timeout: timeout / 2
        });
        const loadTime = Date.now() - startTime;
        const pageTitle = await page.title();
        const currentUrl = page.url();
        console.error(`[SearchEngine] BING: Homepage loaded in ${loadTime}ms, title: "${pageTitle}", URL: ${currentUrl}`);
        // Wait a moment for page to fully load
        await page.waitForTimeout(500);
        // Find and use the search box (more realistic than direct URL)
        try {
            console.error(`[SearchEngine] BING: Looking for search form elements...`);
            await page.waitForSelector('#sb_form_q', { timeout: 2000 });
            console.error(`[SearchEngine] BING: Search box found, filling with query: "${query}"`);
            await page.fill('#sb_form_q', query);
            console.error(`[SearchEngine] BING: Clicking search button and waiting for navigation...`);
            // Submit the search form
            await Promise.all([
                page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: timeout }),
                page.click('#search_icon')
            ]);
            const searchLoadTime = Date.now() - startTime;
            const searchPageTitle = await page.title();
            const searchPageUrl = page.url();
            console.error(`[SearchEngine] BING: Search completed in ${searchLoadTime}ms total, title: "${searchPageTitle}", URL: ${searchPageUrl}`);
        }
        catch (formError) {
            const errorMessage = formError instanceof Error ? formError.message : 'Unknown error';
            console.error(`[SearchEngine] BING: Search form submission failed: ${errorMessage}`);
            if (debugBing) {
                console.error(`[SearchEngine] BING: Form error details:`, formError);
            }
            throw formError;
        }
        // Wait for search results to load
        try {
            console.error(`[SearchEngine] BING: Waiting for search results to appear...`);
            await page.waitForSelector('.b_algo, .b_result', { timeout: 3000 });
            console.error(`[SearchEngine] BING: Search results selector found`);
        }
        catch {
            console.error(`[SearchEngine] BING: Search results selector not found, proceeding with page content anyway`);
        }
        const html = await page.content();
        console.error(`[SearchEngine] BING: Got page HTML with length: ${html.length} characters`);
        if (debugBing && html.length < 10000) {
            console.error(`[SearchEngine] BING: WARNING - HTML seems short, possible bot detection or error page`);
        }
        const results = this.parseBingResults(html, numResults);
        console.error(`[SearchEngine] BING: Enhanced search parsed ${results.length} results`);
        if (results.length === 0) {
            console.error(`[SearchEngine] BING: WARNING - No results found, possible parsing failure or empty search`);
            if (debugBing) {
                const sampleHtml = html.substring(0, 1000);
                console.error(`[SearchEngine] BING: Sample HTML for debugging:`, sampleHtml);
            }
        }
        return results;
    }
    async tryDirectBingSearch(page, query, numResults, timeout) {
        const debugBing = process.env.DEBUG_BING_SEARCH === 'true';
        console.error(`[SearchEngine] BING: Direct search with enhanced parameters...`);
        // Generate a conversation ID (cvid) similar to what Bing uses
        const cvid = this.generateConversationId();
        // Construct URL with enhanced parameters based on successful manual searches
        const searchUrl = `https://www.bing.com/search?q=${encodeURIComponent(query)}&count=${Math.min(numResults, 10)}&form=QBLH&sp=-1&qs=n&cvid=${cvid}`;
        console.error(`[SearchEngine] BING: Navigating to direct URL: ${searchUrl}`);
        const startTime = Date.now();
        await page.goto(searchUrl, {
            waitUntil: 'domcontentloaded',
            timeout: timeout
        });
        const loadTime = Date.now() - startTime;
        const pageTitle = await page.title();
        const currentUrl = page.url();
        console.error(`[SearchEngine] BING: Direct page loaded in ${loadTime}ms, title: "${pageTitle}", URL: ${currentUrl}`);
        // Wait for search results to load
        try {
            console.error(`[SearchEngine] BING: Waiting for search results to appear...`);
            await page.waitForSelector('.b_algo, .b_result', { timeout: 3000 });
            console.error(`[SearchEngine] BING: Search results selector found`);
        }
        catch {
            console.error(`[SearchEngine] BING: Search results selector not found, proceeding with page content anyway`);
        }
        const html = await page.content();
        console.error(`[SearchEngine] BING: Got page HTML with length: ${html.length} characters`);
        if (debugBing && html.length < 10000) {
            console.error(`[SearchEngine] BING: WARNING - HTML seems short, possible bot detection or error page`);
        }
        const results = this.parseBingResults(html, numResults);
        console.error(`[SearchEngine] BING: Direct search parsed ${results.length} results`);
        if (results.length === 0) {
            console.error(`[SearchEngine] BING: WARNING - No results found, possible parsing failure or empty search`);
            if (debugBing) {
                const sampleHtml = html.substring(0, 1000);
                console.error(`[SearchEngine] BING: Sample HTML for debugging:`, sampleHtml);
            }
        }
        return results;
    }
    generateConversationId() {
        // Generate a conversation ID similar to Bing's format (32 hex characters)
        const chars = '0123456789ABCDEF';
        let cvid = '';
        for (let i = 0; i < 32; i++) {
            cvid += chars[Math.floor(Math.random() * chars.length)];
        }
        return cvid;
    }
    async tryDuckDuckGoSearch(query, numResults, timeout) {
        console.log(`[SearchEngine] Trying DuckDuckGo as fallback...`);
        try {
            const response = await axios.get('https://html.duckduckgo.com/html/', {
                params: {
                    q: query,
                },
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                timeout,
                validateStatus: (status) => status < 400,
            });
            console.log(`[SearchEngine] DuckDuckGo got response with status: ${response.status}`);
            const results = this.parseDuckDuckGoResults(response.data, numResults);
            console.log(`[SearchEngine] DuckDuckGo parsed ${results.length} results`);
            return results;
        }
        catch {
            console.error(`[SearchEngine] DuckDuckGo search failed`);
            throw new Error('DuckDuckGo search failed');
        }
    }
    parseSearchResults(html, maxResults) {
        console.log(`[SearchEngine] Parsing HTML with length: ${html.length}`);
        const $ = cheerio.load(html);
        const results = [];
        const timestamp = generateTimestamp();
        // Log what selectors we find - more comprehensive debugging
        const gElements = $('div.g');
        const sokobanElements = $('div[data-sokoban-container]');
        const tF2CxcElements = $('.tF2Cxc');
        const rcElements = $('.rc');
        const vedElements = $('[data-ved]');
        const h3Elements = $('h3');
        const linkElements = $('a[href]');
        console.log(`[SearchEngine] Found elements:`);
        console.log(`  - div.g: ${gElements.length}`);
        console.log(`  - div[data-sokoban-container]: ${sokobanElements.length}`);
        console.log(`  - .tF2Cxc: ${tF2CxcElements.length}`);
        console.log(`  - .rc: ${rcElements.length}`);
        console.log(`  - [data-ved]: ${vedElements.length}`);
        console.log(`  - h3: ${h3Elements.length}`);
        console.log(`  - a[href]: ${linkElements.length}`);
        // Try multiple approaches to find search results
        const searchResultSelectors = [
            'div.g',
            'div[data-sokoban-container]',
            '.tF2Cxc',
            '.rc',
            '[data-ved]',
            'div[jscontroller]'
        ];
        let foundResults = false;
        for (const selector of searchResultSelectors) {
            if (foundResults)
                break;
            console.log(`[SearchEngine] Trying selector: ${selector}`);
            const elements = $(selector);
            console.log(`[SearchEngine] Found ${elements.length} elements with selector ${selector}`);
            elements.each((_index, element) => {
                if (results.length >= maxResults)
                    return false;
                const $element = $(element);
                // Try multiple title selectors
                const titleSelectors = ['h3', '.LC20lb', '.DKV0Md', 'a[data-ved]', '.r', '.s'];
                let title = '';
                let url = '';
                for (const titleSelector of titleSelectors) {
                    const $title = $element.find(titleSelector).first();
                    if ($title.length) {
                        title = $title.text().trim();
                        console.log(`[SearchEngine] Found title with ${titleSelector}: "${title}"`);
                        // Try to find the link
                        const $link = $title.closest('a');
                        if ($link.length) {
                            url = $link.attr('href') || '';
                            console.log(`[SearchEngine] Found URL: "${url}"`);
                        }
                        else {
                            // Try to find any link in the element
                            const $anyLink = $element.find('a[href]').first();
                            if ($anyLink.length) {
                                url = $anyLink.attr('href') || '';
                                console.log(`[SearchEngine] Found URL from any link: "${url}"`);
                            }
                        }
                        break;
                    }
                }
                // Try multiple snippet selectors
                const snippetSelectors = ['.VwiC3b', '.st', '.aCOpRe', '.IsZvec', '.s3v9rd', '.MUxGbd', '.aCOpRe', '.snippet-content'];
                let snippet = '';
                for (const snippetSelector of snippetSelectors) {
                    const $snippet = $element.find(snippetSelector).first();
                    if ($snippet.length) {
                        snippet = $snippet.text().trim();
                        console.log(`[SearchEngine] Found snippet with ${snippetSelector}: "${snippet.substring(0, 100)}..."`);
                        break;
                    }
                }
                if (title && url && this.isValidSearchUrl(url)) {
                    console.log(`[SearchEngine] Adding result: ${title}`);
                    results.push({
                        title,
                        url: this.cleanGoogleUrl(url),
                        description: snippet || 'No description available',
                        fullContent: '',
                        contentPreview: '',
                        wordCount: 0,
                        timestamp,
                        fetchStatus: 'success',
                    });
                    foundResults = true;
                }
                else {
                    console.log(`[SearchEngine] Skipping result: title="${title}", url="${url}", isValid=${this.isValidSearchUrl(url)}`);
                }
            });
        }
        console.log(`[SearchEngine] Found ${results.length} results with all selectors`);
        // If still no results, try a more aggressive approach - look for any h3 with links
        if (results.length === 0) {
            console.log(`[SearchEngine] No results found, trying aggressive h3 search...`);
            $('h3').each((_index, element) => {
                if (results.length >= maxResults)
                    return false;
                const $h3 = $(element);
                const title = $h3.text().trim();
                const $link = $h3.closest('a');
                if ($link.length && title) {
                    const url = $link.attr('href') || '';
                    console.log(`[SearchEngine] Aggressive search found: "${title}" -> "${url}"`);
                    if (this.isValidSearchUrl(url)) {
                        results.push({
                            title,
                            url: this.cleanGoogleUrl(url),
                            description: 'No description available',
                            fullContent: '',
                            contentPreview: '',
                            wordCount: 0,
                            timestamp,
                            fetchStatus: 'success',
                        });
                    }
                }
            });
            console.log(`[SearchEngine] Aggressive search found ${results.length} results`);
        }
        return results;
    }
    parseBraveResults(html, maxResults) {
        console.log(`[SearchEngine] Parsing Brave HTML with length: ${html.length}`);
        const $ = cheerio.load(html);
        const results = [];
        const timestamp = generateTimestamp();
        // Brave result selectors
        const resultSelectors = [
            '[data-type="web"]', // Main Brave results
            '.result', // Alternative format
            '.fdb' // Brave specific format
        ];
        let foundResults = false;
        for (const selector of resultSelectors) {
            if (foundResults && results.length >= maxResults)
                break;
            console.log(`[SearchEngine] Trying Brave selector: ${selector}`);
            const elements = $(selector);
            console.log(`[SearchEngine] Found ${elements.length} elements with selector ${selector}`);
            elements.each((_index, element) => {
                if (results.length >= maxResults)
                    return false;
                const $element = $(element);
                // Try multiple title selectors for Brave
                const titleSelectors = [
                    '.title a', // Brave specific
                    'h2 a', // Common format  
                    '.result-title a', // Alternative format
                    'a[href*="://"]', // Any external link
                    '.snippet-title a' // Snippet title
                ];
                let title = '';
                let url = '';
                for (const titleSelector of titleSelectors) {
                    const $titleElement = $element.find(titleSelector).first();
                    if ($titleElement.length) {
                        title = $titleElement.text().trim();
                        url = $titleElement.attr('href') || '';
                        console.log(`[SearchEngine] Brave found title with ${titleSelector}: "${title}"`);
                        if (title && url && url.startsWith('http')) {
                            break;
                        }
                    }
                }
                // If still no title, try getting it from any text content
                if (!title) {
                    const textContent = $element.text().trim();
                    const lines = textContent.split('\n').filter(line => line.trim().length > 0);
                    if (lines.length > 0) {
                        title = lines[0].trim();
                        console.log(`[SearchEngine] Brave found title from text content: "${title}"`);
                    }
                }
                // Try multiple snippet selectors for Brave
                const snippetSelectors = [
                    '.snippet-content', // Brave specific
                    '.snippet', // Generic
                    '.description', // Alternative
                    'p' // Fallback paragraph
                ];
                let snippet = '';
                for (const snippetSelector of snippetSelectors) {
                    const $snippetElement = $element.find(snippetSelector).first();
                    if ($snippetElement.length) {
                        snippet = $snippetElement.text().trim();
                        break;
                    }
                }
                if (title && url && this.isValidSearchUrl(url)) {
                    console.log(`[SearchEngine] Brave found: "${title}" -> "${url}"`);
                    results.push({
                        title,
                        url: this.cleanBraveUrl(url),
                        description: snippet || 'No description available',
                        fullContent: '',
                        contentPreview: '',
                        wordCount: 0,
                        timestamp,
                        fetchStatus: 'success',
                    });
                    foundResults = true;
                }
            });
        }
        console.log(`[SearchEngine] Brave found ${results.length} results`);
        return results;
    }
    parseGoogleResults(html, maxResults) {
        console.log(`[SearchEngine] Parsing Google HTML with length: ${html.length}`);
        const $ = cheerio.load(html);
        const results = [];
        const timestamp = generateTimestamp();
        // Google result selectors
        const resultSelectors = [
            '#search .g',           // Standard Google results
            '.Gx5Zad',             // Alternative Google result container
            '.tF2Cxc',             // Another variant
            '.g[data-hveid]',      // Results with data attribute
        ];
        let foundResults = false;
        for (const selector of resultSelectors) {
            if (foundResults && results.length >= maxResults)
                break;
            console.log(`[SearchEngine] Trying Google selector: ${selector}`);
            const elements = $(selector);
            console.log(`[SearchEngine] Found ${elements.length} elements with selector ${selector}`);
            elements.each((_index, element) => {
                if (results.length >= maxResults)
                    return false;
                const $element = $(element);
                // Try multiple title/selectors for Google
                const titleSelectors = [
                    'h3',                    // Standard Google title
                    '.LC20lb',              // Google title class
                    '.DKV0Md',              // Another title class
                    'h3 span',              // Title with span
                ];
                let title = '';
                let url = '';
                // Get URL from the parent anchor tag
                const $anchor = $element.find('a[href^="http"]').first();
                if ($anchor.length) {
                    url = $anchor.attr('href') || '';
                }
                for (const titleSelector of titleSelectors) {
                    const $titleElement = $element.find(titleSelector).first();
                    if ($titleElement.length) {
                        title = $titleElement.text().trim();
                        if (title) break;
                    }
                }
                // Try multiple snippet selectors for Google
                const snippetSelectors = [
                    '.VwiC3b',             // Google snippet class
                    '.st',                  // Older snippet class
                    '.IsZvec',             // Alternative
                    '[style*="-webkit-line-clamp"]', // Clamped snippets
                ];
                let snippet = '';
                for (const snippetSelector of snippetSelectors) {
                    const $snippetElement = $element.find(snippetSelector).first();
                    if ($snippetElement.length) {
                        snippet = $snippetElement.text().trim();
                        if (snippet) break;
                    }
                }
                if (title && url && url.startsWith('http') && this.isValidSearchUrl(url)) {
                    console.log(`[SearchEngine] Google found: "${title}" -> "${url}"`);
                    results.push({
                        title,
                        url,
                        description: snippet || 'No description available',
                        fullContent: '',
                        contentPreview: '',
                        wordCount: 0,
                        timestamp,
                        fetchStatus: 'success',
                    });
                    foundResults = true;
                }
            });
        }
        console.log(`[SearchEngine] Google found ${results.length} results`);
        return results;
    }
    parseBingResults(html, maxResults) {
        const debugBing = process.env.DEBUG_BING_SEARCH === 'true';
        console.error(`[SearchEngine] BING: Parsing HTML with length: ${html.length}`);
        const $ = cheerio.load(html);
        const results = [];
        const timestamp = generateTimestamp();
        // Check for common Bing error indicators
        const pageTitle = $('title').text();
        console.error(`[SearchEngine] BING: Page title: "${pageTitle}"`);
        if (pageTitle.includes('Access Denied') || pageTitle.includes('blocked') || pageTitle.includes('captcha')) {
            console.error(`[SearchEngine] BING: ERROR - Bot detection or access denied detected in page title`);
        }
        // Bing result selectors
        const resultSelectors = [
            '.b_algo', // Main Bing results
            '.b_result', // Alternative Bing format
            '.b_card' // Card format
        ];
        console.error(`[SearchEngine] BING: Checking for result elements...`);
        // Log counts for all selectors first
        for (const selector of resultSelectors) {
            const elements = $(selector);
            console.error(`[SearchEngine] BING: Found ${elements.length} elements with selector "${selector}"`);
        }
        let foundResults = false;
        for (const selector of resultSelectors) {
            if (foundResults && results.length >= maxResults)
                break;
            const elements = $(selector);
            if (elements.length === 0)
                continue;
            elements.each((_index, element) => {
                if (results.length >= maxResults)
                    return false;
                const $element = $(element);
                // Try multiple title selectors for Bing
                const titleSelectors = [
                    'h2 a', // Standard Bing format
                    '.b_title a', // Alternative format
                    'a[data-seid]' // Bing specific
                ];
                let title = '';
                let url = '';
                for (const titleSelector of titleSelectors) {
                    const $titleElement = $element.find(titleSelector).first();
                    if ($titleElement.length) {
                        title = $titleElement.text().trim();
                        url = $titleElement.attr('href') || '';
                        console.log(`[SearchEngine] Bing found title with ${titleSelector}: "${title}"`);
                        break;
                    }
                }
                // Try multiple snippet selectors for Bing
                const snippetSelectors = [
                    '.b_caption p', // Standard Bing snippet
                    '.b_snippet', // Alternative format
                    '.b_descript', // Description format
                    '.b_caption', // Caption without p tag
                    '.b_caption > span', // Caption span
                    '.b_excerpt', // Excerpt format
                    'p', // Any paragraph in the result
                    '.b_algo_content p', // Content paragraph
                    '.b_algo_content', // Full content area
                    '.b_context' // Context information
                ];
                let snippet = '';
                for (const snippetSelector of snippetSelectors) {
                    const $snippetElement = $element.find(snippetSelector).first();
                    if ($snippetElement.length) {
                        const candidateSnippet = $snippetElement.text().trim();
                        // Skip very short snippets or those that look like metadata
                        if (candidateSnippet.length > 20 && !candidateSnippet.match(/^\d+\s*(min|sec|hour|day|week|month|year)/i)) {
                            snippet = candidateSnippet;
                            console.log(`[SearchEngine] Bing found snippet with ${snippetSelector}: "${snippet.substring(0, 100)}..."`);
                            break;
                        }
                    }
                }
                if (title && url && this.isValidSearchUrl(url)) {
                    console.log(`[SearchEngine] Bing found: "${title}" -> "${url}"`);
                    results.push({
                        title,
                        url: this.cleanBingUrl(url),
                        description: snippet || 'No description available',
                        fullContent: '',
                        contentPreview: '',
                        wordCount: 0,
                        timestamp,
                        fetchStatus: 'success',
                    });
                    foundResults = true;
                }
            });
        }
        console.log(`[SearchEngine] Bing found ${results.length} results`);
        return results;
    }
    parseDuckDuckGoResults(html, maxResults) {
        console.log(`[SearchEngine] Parsing DuckDuckGo HTML with length: ${html.length}`);
        const $ = cheerio.load(html);
        const results = [];
        const timestamp = generateTimestamp();
        // DuckDuckGo results are in .result elements
        $('.result').each((_index, element) => {
            if (results.length >= maxResults)
                return false;
            const $element = $(element);
            // Extract title and URL
            const $titleElement = $element.find('.result__title a');
            const title = $titleElement.text().trim();
            const url = $titleElement.attr('href');
            // Extract snippet
            const snippet = $element.find('.result__snippet').text().trim();
            if (title && url) {
                console.log(`[SearchEngine] DuckDuckGo found: "${title}" -> "${url}"`);
                results.push({
                    title,
                    url: this.cleanDuckDuckGoUrl(url),
                    description: snippet || 'No description available',
                    fullContent: '',
                    contentPreview: '',
                    wordCount: 0,
                    timestamp,
                    fetchStatus: 'success',
                });
            }
        });
        console.log(`[SearchEngine] DuckDuckGo found ${results.length} results`);
        return results;
    }
    isValidSearchUrl(url) {
        // Google search results URLs can be in various formats
        return url.startsWith('/url?') ||
            url.startsWith('http://') ||
            url.startsWith('https://') ||
            url.startsWith('//') ||
            url.startsWith('/search?') ||
            url.startsWith('/') ||
            url.includes('google.com') ||
            url.length > 10; // Accept any reasonably long URL
    }
    cleanGoogleUrl(url) {
        // Handle Google's redirect URLs
        if (url.startsWith('/url?')) {
            try {
                const urlParams = new URLSearchParams(url.substring(5));
                const actualUrl = urlParams.get('q') || urlParams.get('url');
                if (actualUrl) {
                    return actualUrl;
                }
            }
            catch {
                console.warn('Failed to parse Google redirect URL:', url);
            }
        }
        // Handle protocol-relative URLs
        if (url.startsWith('//')) {
            return 'https:' + url;
        }
        return url;
    }
    cleanBraveUrl(url) {
        // Brave URLs are usually direct, but check for any redirect patterns
        if (url.startsWith('//')) {
            return 'https:' + url;
        }
        // If it's already a full URL, return as-is
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        return url;
    }
    cleanBingUrl(url) {
        // Bing URLs are usually direct, but check for any redirect patterns
        if (url.startsWith('//')) {
            return 'https:' + url;
        }
        // If it's already a full URL, return as-is
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        return url;
    }
    cleanDuckDuckGoUrl(url) {
        // DuckDuckGo URLs are redirect URLs that need to be decoded
        if (url.startsWith('//duckduckgo.com/l/')) {
            try {
                // Extract the uddg parameter which contains the actual URL
                const urlParams = new URLSearchParams(url.substring(url.indexOf('?') + 1));
                const actualUrl = urlParams.get('uddg');
                if (actualUrl) {
                    // Decode the URL
                    const decodedUrl = decodeURIComponent(actualUrl);
                    console.log(`[SearchEngine] Decoded DuckDuckGo URL: ${decodedUrl}`);
                    return decodedUrl;
                }
            }
            catch {
                console.log(`[SearchEngine] Failed to decode DuckDuckGo URL: ${url}`);
            }
        }
        // If it's a protocol-relative URL, add https:
        if (url.startsWith('//')) {
            return 'https:' + url;
        }
        return url;
    }
    assessResultQuality(results, originalQuery) {
        if (results.length === 0)
            return 0;
        // Extract keywords from the original query (ignore common words)
        const commonWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'group', 'members']);
        const queryWords = originalQuery.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 2 && !commonWords.has(word));
        if (queryWords.length === 0)
            return 0.5; // Default score if no meaningful keywords
        console.log(`[SearchEngine] Quality assessment - Query keywords: [${queryWords.join(', ')}]`);
        let totalScore = 0;
        let scoredResults = 0;
        for (const result of results) {
            const titleText = result.title.toLowerCase();
            const descText = result.description.toLowerCase();
            const urlText = result.url.toLowerCase();
            const combinedText = `${titleText} ${descText} ${urlText}`;
            // Count keyword matches
            let keywordMatches = 0;
            let phraseMatches = 0;
            // Check for exact phrase matches (higher value)
            if (queryWords.length >= 2) {
                const queryPhrases = [];
                for (let i = 0; i < queryWords.length - 1; i++) {
                    queryPhrases.push(queryWords.slice(i, i + 2).join(' '));
                }
                if (queryWords.length >= 3) {
                    queryPhrases.push(queryWords.slice(0, 3).join(' '));
                }
                for (const phrase of queryPhrases) {
                    if (combinedText.includes(phrase)) {
                        phraseMatches++;
                    }
                }
            }
            // Check individual keyword matches
            for (const keyword of queryWords) {
                if (combinedText.includes(keyword)) {
                    keywordMatches++;
                }
            }
            // Calculate score for this result
            const keywordRatio = keywordMatches / queryWords.length;
            const phraseBonus = phraseMatches * 0.3; // Bonus for phrase matches
            const resultScore = Math.min(1.0, keywordRatio + phraseBonus);
            // Penalty for obvious irrelevant content
            const irrelevantPatterns = [
                /recipe/i, /cooking/i, /food/i, /restaurant/i, /menu/i,
                /weather/i, /temperature/i, /forecast/i,
                /shopping/i, /sale/i, /price/i, /buy/i, /store/i,
                /movie/i, /film/i, /tv show/i, /entertainment/i,
                /sports/i, /game/i, /score/i, /team/i,
                /fashion/i, /clothing/i, /style/i,
                /travel/i, /hotel/i, /flight/i, /vacation/i,
                /car/i, /vehicle/i, /automotive/i,
                /real estate/i, /property/i, /house/i, /apartment/i
            ];
            let penalty = 0;
            for (const pattern of irrelevantPatterns) {
                if (pattern.test(combinedText)) {
                    penalty += 0.2;
                }
            }
            const finalScore = Math.max(0, resultScore - penalty);
            console.log(`[SearchEngine] Result "${result.title.substring(0, 50)}..." - Score: ${finalScore.toFixed(2)} (keywords: ${keywordMatches}/${queryWords.length}, phrases: ${phraseMatches}, penalty: ${penalty.toFixed(2)})`);
            totalScore += finalScore;
            scoredResults++;
        }
        const averageScore = scoredResults > 0 ? totalScore / scoredResults : 0;
        return averageScore;
    }
    async validateBrowserHealth(browser) {
        const debugBrowsers = process.env.DEBUG_BROWSER_LIFECYCLE === 'true';
        try {
            if (debugBrowsers)
                console.log(`[SearchEngine] Validating browser health...`);
            // Check if browser is still connected
            if (!browser.isConnected()) {
                if (debugBrowsers)
                    console.log(`[SearchEngine] Browser is not connected`);
                return false;
            }
            // Try to create a simple context to test browser responsiveness
            const testContext = await browser.newContext();
            await testContext.close();
            if (debugBrowsers)
                console.log(`[SearchEngine] Browser health check passed`);
            return true;
        }
        catch (error) {
            console.log(`[SearchEngine] Browser health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            return false;
        }
    }
    async handleBrowserError(error, engineName, attemptNumber = 1) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.error(`[SearchEngine] ${engineName} browser error (attempt ${attemptNumber}): ${errorMessage}`);
        // Check for specific browser-related errors
        if (errorMessage.includes('Target page, context or browser has been closed') ||
            errorMessage.includes('Browser has been closed') ||
            errorMessage.includes('Session has been closed')) {
            console.log(`[SearchEngine] Detected browser session closure, attempting to refresh browser pool`);
            // Try to refresh the browser pool for subsequent attempts
            try {
                await this.browserPool.closeAll();
                console.log(`[SearchEngine] Browser pool refreshed for ${engineName}`);
            }
            catch (refreshError) {
                console.error(`[SearchEngine] Failed to refresh browser pool: ${refreshError instanceof Error ? refreshError.message : 'Unknown error'}`);
            }
        }
    }
    async closeAll() {
        await this.browserPool.closeAll();
    }
}
//# sourceMappingURL=search-engine.js.map