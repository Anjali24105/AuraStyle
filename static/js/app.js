/* ==========================================================================
   AuraStyle SPA Controller - Multimodal Search, Voice Transcription & DOM
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Inputs & Controls
    const searchInput = document.getElementById('searchInput');
    const voiceSearchBtn = document.getElementById('voiceSearchBtn');
    const imageInput = document.getElementById('imageInput');
    const dropZone = document.getElementById('dropZone');
    const dropZonePrompt = document.getElementById('dropZonePrompt');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const clearImageBtn = document.getElementById('clearImageBtn');
    
    // Sliders & Weighting
    const weightControlsPanel = document.getElementById('weightControlsPanel');
    const searchWeightSlider = document.getElementById('searchWeightSlider');
    const weightValText = document.getElementById('weightValText');
    
    // Actions & Displays
    const searchSubmitBtn = document.getElementById('searchSubmitBtn');
    const resetSearchBtn = document.getElementById('resetSearchBtn');
    const adminReindexBtn = document.getElementById('adminReindexBtn');
    const catalogTitle = document.getElementById('catalogTitle');
    const resultsMetaText = document.getElementById('resultsMetaText');
    const loaderContainer = document.getElementById('loaderContainer');
    const productGrid = document.getElementById('productGrid');
    const emptyState = document.getElementById('emptyState');
    const toast = document.getElementById('toast');

    // State Variables
    let selectedImageFile = null;
    let isRecording = false;
    let speechRecognitionInstance = null;

    // Initialize Web Speech API for voice search
    initVoiceRecognition();
    
    // Fetch and display full product catalog on initial load
    fetchCatalog();

    /* ==========================================================================
       1. Database Catalog Loading & Dynamic Card Renderer
       ========================================================================== */

    /**
     * Fetches all products from Flask API and renders them.
     */
    async function fetchCatalog() {
        showLoader(true);
        catalogTitle.textContent = "Latest Styles";
        resultsMetaText.textContent = "";
        resetSearchBtn.style.display = "none";
        
        try {
            const response = await fetch('/api/products');
            if (!response.ok) throw new Error("Catalog fetch failed.");
            const products = await response.json();
            renderProducts(products, false);
        } catch (err) {
            console.error(err);
            showToast("Failed to fetch product catalog from server.", "error");
            renderProducts([], false);
        } finally {
            showLoader(false);
        }
    }

    /**
     * Renders array of products as HTML cards into the masonry container.
     * @param {Array} products - List of product objects.
     * @param {Boolean} isSearchResult - True if rendering search matches (shows similarity score).
     */
    function renderProducts(products, isSearchResult = false) {
        productGrid.innerHTML = "";
        
        if (!products || products.length === 0) {
            emptyState.style.display = "block";
            return;
        }
        
        emptyState.style.display = "none";
        
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            
            // Build rating stars HTML based on the rating value
            const starsHTML = generateStarsHTML(product.rating || 4.5);
            
            // Generate match badge if it's a multimodal search result
            let matchBadgeHTML = "";
            if (isSearchResult && product.similarity_score !== undefined) {
                const scorePercentage = Math.round(product.similarity_score * 100);
                const scoreClass = scorePercentage >= 75 ? 'match-high' : 'match-mid';
                matchBadgeHTML = `
                    <div class="match-badge ${scoreClass}">
                        <i class="fa-solid fa-circle-check"></i>
                        <span>${scorePercentage}% Match</span>
                    </div>
                `;
            }

            card.innerHTML = `
                ${matchBadgeHTML}
                <div class="card-img-wrapper">
                    <!-- Standard image tag with failure handler to load a stylized vector gradient fallback -->
                    <img src="${product.image_path}" 
                         alt="${product.name}" 
                         class="product-img" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="product-img-fallback" style="display: none;">
                        <i class="fa-solid fa-shirt"></i>
                        <span>Style Image Unavailable</span>
                    </div>
                </div>
                <div class="card-body">
                    <span class="card-category">${product.category || 'Apparel'}</span>
                    <h3 class="card-title">${product.name}</h3>
                    <p class="card-desc">${product.description || 'No description available.'}</p>
                    <div class="card-footer">
                        <span class="card-price">$${(product.price || 0.00).toFixed(2)}</span>
                        <div class="card-rating">
                            ${starsHTML}
                            <span class="rating-value">${product.rating || '4.5'}</span>
                        </div>
                    </div>
                </div>
            `;
            
            productGrid.appendChild(card);
        });
    }

    /**
     * Generates FontAwesome star icons structure.
     * @param {Number} rating - Value out of 5.
     */
    function generateStarsHTML(rating) {
        let stars = "";
        const fullStars = Math.floor(rating);
        const hasHalf = rating % 1 !== 0;
        
        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars += '<i class="fa-solid fa-star rating-star"></i>';
            } else if (i === fullStars && hasHalf) {
                stars += '<i class="fa-solid fa-star-half-stroke rating-star"></i>';
            } else {
                stars += '<i class="fa-regular fa-star rating-star"></i>';
            }
        }
        return stars;
    }

    /* ==========================================================================
       2. Web Speech API - Voice Transcription Section
       ========================================================================== */

    function initVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            console.warn("Speech recognition not supported in this browser.");
            voiceSearchBtn.style.display = "none";
            return;
        }

        speechRecognitionInstance = new SpeechRecognition();
        speechRecognitionInstance.continuous = false;
        speechRecognitionInstance.lang = 'en-US';
        speechRecognitionInstance.interimResults = false;
        speechRecognitionInstance.maxAlternatives = 1;

        // When recording triggers
        speechRecognitionInstance.onstart = () => {
            isRecording = true;
            voiceSearchBtn.classList.add('recording');
            searchInput.placeholder = "Listening for style details...";
        };

        // On complete
        speechRecognitionInstance.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            searchInput.value = transcript;
            showToast(`Voice matched: "${transcript}"`, "success");
            
            // Stop speech recognition immediately before running search to avoid state conflicts
            speechRecognitionInstance.stop();
            
            // Automatically execute search
            executeSearch();
        };

        speechRecognitionInstance.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            if (event.error === 'not-allowed') {
                showToast("Microphone access is blocked. Please enable it in your browser settings.", "error");
            } else if (event.error === 'no-speech') {
                showToast("No speech was detected. Please speak clearly into the microphone.", "info");
            } else {
                showToast(`Speech recognition error: ${event.error}`, "error");
            }
        };

        speechRecognitionInstance.onend = () => {
            isRecording = false;
            voiceSearchBtn.classList.remove('recording');
            searchInput.placeholder = "Describe the style, color, or vibe you're looking for...";
        };

        // Mic click action listener with explicit permission checking
        voiceSearchBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (isRecording) {
                speechRecognitionInstance.stop();
            } else {
                // Explicitly request microphone permission
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    navigator.mediaDevices.getUserMedia({ audio: true })
                        .then((stream) => {
                            // Permission granted: close prompt audio stream immediately to release hardware
                            stream.getTracks().forEach(track => track.stop());
                            // Initialize speech recognition
                            speechRecognitionInstance.start();
                        })
                        .catch((err) => {
                            console.error("Microphone permission denied:", err);
                            showToast("Microphone access denied. Please enable microphone permissions in your browser settings.", "error");
                        });
                } else {
                    // Fallback direct invocation if getUserMedia is not supported
                    try {
                        speechRecognitionInstance.start();
                    } catch (err) {
                        console.error("Failed to start SpeechRecognition:", err);
                        showToast("Unable to start speech recognition in this environment.", "error");
                    }
                }
            }
        });
    }

    /* ==========================================================================
       3. Drag and Drop File Uploads handlers
       ========================================================================== */

    // Browse click trigger
    dropZone.addEventListener('click', () => {
        if (!selectedImageFile) {
            imageInput.click();
        }
    });

    imageInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files[0]);
    });

    // Drag-over styling
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    /**
     * Stores selected file and renders the image preview inside the zone.
     * Activates the weight slider for multimodal search blending.
     */
    function handleFileSelection(file) {
        if (!file) return;
        
        // Verify format
        if (!file.type.startsWith('image/')) {
            showToast("Invalid file type. Please upload a fashion image.", "error");
            return;
        }
        
        selectedImageFile = file;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZonePrompt.style.display = 'none';
            previewContainer.style.display = 'flex';
            
            // Show weights panel for multimodal combined search
            weightControlsPanel.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    // Clear image button action
    clearImageBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Avoid triggering browser browse action on dropzone
        selectedImageFile = null;
        imageInput.value = "";
        imagePreview.src = "";
        previewContainer.style.display = 'none';
        dropZonePrompt.style.display = 'flex';
        
        // Hide weights panel if no image is present
        weightControlsPanel.style.display = 'none';
    });

    /* ==========================================================================
       4. Multimodal Balance Slider
       ========================================================================== */

    searchWeightSlider.addEventListener('input', (e) => {
        const val = e.target.value;
        const textWeight = 100 - val;
        const imageWeight = val;
        weightValText.textContent = `${textWeight}% Text / ${imageWeight}% Image`;
    });

    /* ==========================================================================
       5. Multimodal Search execution
       ========================================================================== */

    searchSubmitBtn.addEventListener('click', executeSearch);

    async function executeSearch() {
        const textQuery = searchInput.value.trim();
        const imagePresent = selectedImageFile !== null;

        if (!textQuery && !imagePresent) {
            showToast("Please enter a text description or upload a style photo.", "info");
            return;
        }

        showLoader(true);
        productGrid.innerHTML = "";
        emptyState.style.display = "none";
        
        // Assemble Multi-part FormData
        const formData = new FormData();
        if (textQuery) formData.append('text', textQuery);
        if (imagePresent) formData.append('image', selectedImageFile);

        // Compute weights ratio
        if (textQuery && imagePresent) {
            const imageWeightRatio = searchWeightSlider.value / 100;
            const textWeightRatio = 1.0 - imageWeightRatio;
            formData.append('text_weight', textWeightRatio);
            formData.append('image_weight', imageWeightRatio);
        }

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Search error.");
            }

            const results = await response.json();
            
            // Render results
            catalogTitle.textContent = "Matched Trends";
            resultsMetaText.textContent = `Found ${results.length} styles`;
            resetSearchBtn.style.display = "block";
            
            renderProducts(results, true);
            showToast("Similarity matches generated.", "success");
        } catch (err) {
            console.error(err);
            showToast(err.message || "Search failed. Verify model is active.", "error");
            catalogTitle.textContent = "Search Failed";
            renderProducts([], false);
        } finally {
            showLoader(false);
        }
    }

    // Reset search to full catalog view
    resetSearchBtn.addEventListener('click', () => {
        searchInput.value = "";
        if (selectedImageFile) {
            clearImageBtn.click();
        }
        fetchCatalog();
    });

    /* ==========================================================================
       6. Administrative Database Reindexing trigger
       ========================================================================== */

    adminReindexBtn.addEventListener('click', async () => {
        const confirmReindex = confirm("Do you want to re-compute CLIP embeddings for all local catalog images? This may take some time depending on your system hardware.");
        if (!confirmReindex) return;
        
        showLoader(true);
        showToast("Starting administrative CLIP reindexing...", "info");
        
        try {
            const response = await fetch('/api/admin/reindex', {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error("Reindexing request failed.");
            const data = await response.json();
            
            showToast(`Reindexing complete! Success: ${data.indexed_count}, Skipped: ${data.skipped_count}`, "success");
            
            // Reload catalog
            fetchCatalog();
        } catch (err) {
            console.error(err);
            showToast("Failed to complete administrative reindexing.", "error");
            showLoader(false);
        }
    });

    /* ==========================================================================
       7. General Helper Functions
       ========================================================================== */

    function showLoader(visible) {
        loaderContainer.style.display = visible ? 'flex' : 'none';
        searchSubmitBtn.disabled = visible;
        if (visible) {
            searchSubmitBtn.classList.add('loading');
        } else {
            searchSubmitBtn.classList.remove('loading');
        }
    }

    function showToast(message, type = "info") {
        toast.className = `toast-notification ${type} show`;
        toast.textContent = message;
        
        // Clear previous timeouts if any
        if (toast.timeoutId) {
            clearTimeout(toast.timeoutId);
        }
        
        toast.timeoutId = setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }
});
