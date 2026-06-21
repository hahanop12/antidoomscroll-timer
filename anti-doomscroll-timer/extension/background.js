// Keep a connection port to the native host
let port = null;
let lastSentUrl = '';

// Connect to the native messaging host
function connectToNativeHost() {
    try {
        port = chrome.runtime.connectNative('com.antidoomscroll.timer');
        
        port.onMessage.addListener((message) => {
            console.log('Received from native host:', message);
        });

        port.onDisconnect.addListener(() => {
            console.warn('Native host disconnected. Error:', chrome.runtime.lastError);
            port = null;
        });
    } catch (e) {
        console.error('Error connecting to native host:', e);
        port = null;
    }
}

// Send the URL to the native host
function sendUrlToNative(url) {
    // Normalise URL to avoid duplicate events for the same video
    // (e.g. query parameters, trailing slashes)
    try {
        const urlObj = new URL(url);
        let cleanUrl = urlObj.origin + urlObj.pathname;

        // Preserve the 'v' parameter for YouTube watch URLs to differentiate videos
        if (urlObj.hostname.includes('youtube.com') && urlObj.pathname === '/watch' && urlObj.searchParams.has('v')) {
            cleanUrl += '?v=' + urlObj.searchParams.get('v');
        }

        if (cleanUrl === lastSentUrl) {
            return; // Skip duplicate events
        }

        lastSentUrl = cleanUrl;
        console.log('Sending URL to native host:', cleanUrl);

        if (!port) {
            connectToNativeHost();
        }

        if (port) {
            port.postMessage({ url: cleanUrl });
        }
    } catch (e) {
        console.error('Error parsing or sending URL:', e);
    }
}

// Monitor tab updates (for general navigation/loading)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
        checkUrl(changeInfo.url);
    }
});

// Monitor history state updates (crucial for SPAs like YouTube/Instagram where page doesn't reload)
chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
    if (details.url) {
        checkUrl(details.url);
    }
});

// Check if the URL is a Short, Reel, or YouTube Watch video
function checkUrl(url) {
    if (url.includes('/shorts/') || url.includes('/reels/') || url.includes('/watch?v=')) {
        sendUrlToNative(url);
    }
}

// Establish connection on startup
connectToNativeHost();

