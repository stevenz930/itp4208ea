
document.addEventListener('DOMContentLoaded', function() {
    // Mobile filter sidebar toggle
    const mobileFilterBtn = document.getElementById('mobileFilterBtn');
    const filterSidebar = document.getElementById('filterSidebar');
    const filterOverlay = document.getElementById('filterOverlay');
    const closeFilterSidebar = document.getElementById('closeFilterSidebar');

    function toggleMobileFilters() {
        filterSidebar.classList.toggle('show');
        filterOverlay.style.display = filterSidebar.classList.contains('show') ? 'block' : 'none';
        document.body.style.overflow = filterSidebar.classList.contains('show') ? 'hidden' : 'auto';
    }

    if (mobileFilterBtn) mobileFilterBtn.addEventListener('click', toggleMobileFilters);
    if (closeFilterSidebar) closeFilterSidebar.addEventListener('click', toggleMobileFilters);
    if (filterOverlay) filterOverlay.addEventListener('click', toggleMobileFilters);

    // Filter application function
    function applyFilters() {
        const activeForm = document.querySelector('.filter-sidebar.show form') || 
                         document.getElementById('desktopFilterForm');
        
        if (!activeForm) return;
        
        const urlParams = new URLSearchParams();
        const currentParams = new URLSearchParams(window.location.search);

        // Handle category filters
        const categoryCheckboxes = activeForm.querySelectorAll('input[name="category"]:checked');
        categoryCheckboxes.forEach(checkbox => {
            urlParams.append('category', checkbox.value);
        });

        // Handle level filters
        const levelCheckboxes = activeForm.querySelectorAll('input[name="level"]:checked');
        levelCheckboxes.forEach(checkbox => {
            urlParams.append('level', checkbox.value);
        });

        // Handle price range
        const minPrice = activeForm.querySelector('input[name="min_price"]').value || '0';
        const maxPrice = activeForm.querySelector('input[name="max_price"]').value || '100';
        urlParams.set('min_price', minPrice);
        urlParams.set('max_price', maxPrice);

        // Preserve subject if exists
        const currentSubject = currentParams.get('subject');
        if (currentSubject) {
            urlParams.set('subject', currentSubject);
        }

        // Preserve sort if exists
        const currentSort = currentParams.get('sort');
        if (currentSort) {
            urlParams.set('sort', currentSort);
        }

        // Reset to first page
        urlParams.set('page', '1');

        // Close mobile filters if open
        if (filterSidebar.classList.contains('show')) {
            toggleMobileFilters();
        }

        window.location.search = urlParams.toString();
    }

    // Price slider setup
    function setupPriceSlider(slider, display, input, progress) {
        if (!slider || !display || !input) return;
        
        slider.addEventListener('input', function() {
            const value = this.value;
            display.textContent = `$${value}`;
            input.value = value;
            if (progress) {
                progress.style.width = `${(value / slider.max) * 100}%`;
            }
        });
        
        slider.addEventListener('change', applyFilters);
    }

    // Initialize sliders
    setupPriceSlider(
        document.getElementById('priceSlider'),
        document.getElementById('maxPriceDisplay'),
        document.getElementById('maxPriceInput'),
        document.querySelector('.price-progress')
    );
    
    setupPriceSlider(
        document.getElementById('desktopPriceSlider'),
        document.getElementById('desktopMaxPriceDisplay'),
        document.getElementById('desktopMaxPriceInput'),
        document.getElementById('desktopPriceProgress')
    );

    // Checkbox setup
    function setupCheckboxes() {
        const urlParams = new URLSearchParams(window.location.search);
        
        document.querySelectorAll('input[type="checkbox"][name="category"], input[type="checkbox"][name="level"]').forEach(checkbox => {
            checkbox.checked = urlParams.getAll(checkbox.name).includes(checkbox.value);
            
            checkbox.addEventListener('change', applyFilters);
        });

        // Initialize price values from URL
        const maxPrice = urlParams.get('max_price') || 
                        document.getElementById('priceSlider')?.max || 
                        document.getElementById('desktopPriceSlider')?.max || 
                        '100';
        
        const minPrice = urlParams.get('min_price') || '0';

        // Update mobile price display
        if (document.getElementById('maxPriceInput')) {
            document.getElementById('maxPriceInput').value = maxPrice;
            document.getElementById('minPriceInput').value = minPrice;
            document.getElementById('maxPriceDisplay').textContent = `$${maxPrice}`;
            if (document.getElementById('priceSlider')) {
                document.getElementById('priceSlider').value = maxPrice;
            }
        }
        
        // Update desktop price display
        if (document.getElementById('desktopMaxPriceInput')) {
            document.getElementById('desktopMaxPriceInput').value = maxPrice;
            document.getElementById('desktopMinPriceInput').value = minPrice;
            document.getElementById('desktopMaxPriceDisplay').textContent = `$${maxPrice}`;
            if (document.getElementById('desktopPriceSlider')) {
                document.getElementById('desktopPriceSlider').value = maxPrice;
            }
        }
    }

    // Sort dropdown initialization
    function initializeSortDropdown() {
        const sortDropdown = document.getElementById('sortDropdown');
        if (!sortDropdown) return;

        const urlParams = new URLSearchParams(window.location.search);
        const currentSort = urlParams.get('sort') || 'popular';
        const sortTextMap = {
            'popular': 'Most Popular',
            'highest': 'Highest Rated',
            'newest': 'Newest',
            'price_low': 'Price Low to High',
            'price_high': 'Price High to Low'
        };

        // Update dropdown text
        const dropdownText = sortTextMap[currentSort] || 'Most Popular';
        sortDropdown.innerHTML = `Sort by: ${dropdownText}`;
    }

    // Initialize everything
    setupCheckboxes();
    initializeSortDropdown();
});