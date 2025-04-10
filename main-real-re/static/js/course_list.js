document.addEventListener('DOMContentLoaded', function() {
    // Mobile filter sidebar elements
    const mobileFilterBtn = document.getElementById('mobileFilterBtn');
    const filterSidebar = document.getElementById('filterSidebar');
    const filterOverlay = document.getElementById('filterOverlay');
    const closeFilterSidebar = document.getElementById('closeFilterSidebar');

    // Mobile filter sidebar toggle
    function closeMobileFilters() {
        filterSidebar?.classList.remove('show');
        if (filterOverlay) {
            filterOverlay.style.display = 'none';
        }
        document.body.style.overflow = 'auto';
    }

    if (mobileFilterBtn && filterSidebar && filterOverlay) {
        mobileFilterBtn.addEventListener('click', function() {
            filterSidebar.classList.add('show');
            filterOverlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });

        closeFilterSidebar?.addEventListener('click', closeMobileFilters);
        filterOverlay.addEventListener('click', closeMobileFilters);
    }

    // Handle filter changes (including price range)
    function updateFilters() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Update price range parameters
        const desktopMinPrice = document.getElementById('desktopMinPriceInput')?.value;
        const desktopMaxPrice = document.getElementById('desktopMaxPriceInput')?.value;
        const mobileMinPrice = document.getElementById('minPriceInput')?.value;
        const mobileMaxPrice = document.getElementById('maxPriceInput')?.value;
        
        if (desktopMinPrice && desktopMaxPrice) {
            urlParams.set('min_price', desktopMinPrice);
            urlParams.set('max_price', desktopMaxPrice);
        } else if (mobileMinPrice && mobileMaxPrice) {
            urlParams.set('min_price', mobileMinPrice);
            urlParams.set('max_price', mobileMaxPrice);
        }
        
        // Reset to first page when filters change
        urlParams.set('page', '1');
        
        // Close mobile filters if needed
        if (window.innerWidth < 992) {
            closeMobileFilters();
        }
        
        // Update URL and reload
        window.location.search = urlParams.toString();
    }

    // Handle checkbox changes
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', updateFilters);
    });

    // Initialize price sliders with new behavior
    function initializeSlider(slider, maxDisplay, maxInput, minInput = null) {
        if (slider) {
            const maxValue = slider.max;
            const currentValue = slider.value;
            
            // Update progress display (if exists)
            const progress = slider.parentElement.querySelector('.price-progress');
            if (progress) {
                progress.style.width = `${(currentValue / maxValue) * 100}%`;
            }
            
            slider.addEventListener('input', function() {
                const value = this.value;
                const max = this.max;
                
                // Update progress display (if exists)
                if (progress) {
                    progress.style.width = `${(value / max) * 100}%`;
                }
                
                // Update display values
                if (maxDisplay) {
                    maxDisplay.textContent = `$${value}`;
                }
                if (maxInput) {
                    maxInput.value = value;
                }
            });
            
            // Change to use our updateFilters function instead of direct form submit
            slider.addEventListener('change', updateFilters);
        }
    }

    // Initialize both sliders
    initializeSlider(
        document.getElementById('priceSlider'),
        document.getElementById('maxPriceDisplay'),
        document.getElementById('maxPriceInput'),
        document.getElementById('minPriceInput')
    );

    initializeSlider(
        document.getElementById('desktopPriceSlider'),
        document.getElementById('desktopMaxPriceDisplay'),
        document.getElementById('desktopMaxPriceInput'),
        document.getElementById('desktopMinPriceInput')
    );

    // Initialize checkbox states from URL
    function updateCheckboxStates() {
        const urlParams = new URLSearchParams(window.location.search);

        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            const paramName = checkbox.name;
            const paramValue = checkbox.value;

            checkbox.checked = urlParams.getAll(paramName).includes(paramValue);
        });
    }
    updateCheckboxStates();
});


document.addEventListener('DOMContentLoaded', function () {
    // Mobile filter sidebar toggle
    const mobileFilterBtn = document.getElementById('mobileFilterBtn');
    const filterSidebar = document.getElementById('filterSidebar');
    const filterOverlay = document.getElementById('filterOverlay');
    const closeFilterSidebar = document.getElementById('closeFilterSidebar');
    

    mobileFilterBtn.addEventListener('click', function () {
        filterSidebar.classList.add('show');
        filterOverlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    });

    function closeMobileFilters() {
        filterSidebar.classList.remove('show');
        filterOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    closeFilterSidebar.addEventListener('click', closeMobileFilters);
    filterOverlay.addEventListener('click', closeMobileFilters);

    // Toggle all filters button
    const toggleAllBtn = document.getElementById('toggleAllFilters');
    const allCollapses = document.querySelectorAll('.filter-sidebar .collapse');
    let allExpanded = false;

    if (toggleAllBtn) {
        toggleAllBtn.addEventListener('click', function () {
            allExpanded = !allExpanded;

            if (allExpanded) {
                toggleAllBtn.querySelector('span').textContent = 'Collapse All';
                toggleAllBtn.querySelector('i').className = 'fas fa-chevron-up ms-1';
            } else {
                toggleAllBtn.querySelector('span').textContent = 'Expand All';
                toggleAllBtn.querySelector('i').className = 'fas fa-chevron-down ms-1';
            }

            allCollapses.forEach(collapse => {
                const bsCollapse = new bootstrap.Collapse(collapse, {
                    toggle: true
                });
            });
        });
    }

    // Rotate chevron icons when individual filters are toggled
    document.querySelectorAll('.btn-filter').forEach(btn => {
        btn.addEventListener('click', function () {
            const icon = this.querySelector('i');
            const isExpanded = this.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                icon.style.transform = 'rotate(0deg)';
            } else {
                icon.style.transform = 'rotate(180deg)';
            }
        });
    });

    // Handle filter changes
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const urlParams = new URLSearchParams(window.location.search);
            const filterName = this.name;
            const filterValue = this.value;

            // Get all currently checked boxes of this filter type
            const checkedBoxes = Array.from(document.querySelectorAll(`input[name="${filterName}"]:checked`));

            // Remove all existing parameters for this filter
            urlParams.delete(filterName);

            // Add back all checked boxes of this filter type
            checkedBoxes.forEach(checkedBox => {
                urlParams.append(filterName, checkedBox.value);
            });

            // If this checkbox was just unchecked, make sure it's not in the URL
            if (!this.checked && urlParams.getAll(filterName).includes(filterValue)) {
                const values = urlParams.getAll(filterName).filter(v => v !== filterValue);
                urlParams.delete(filterName);
                values.forEach(v => urlParams.append(filterName, v));
            }

            // Reset to first page when filters change
            urlParams.set('page', '1');

            // Close mobile filters if in mobile view
            if (window.innerWidth < 992) {
                closeMobileFilters();
            }

            // Submit the form with updated parameters
            window.location.search = urlParams.toString();
        });
    });

    // Initialize checkbox states from URL
    function updateCheckboxStates() {
        const urlParams = new URLSearchParams(window.location.search);

        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            const paramName = checkbox.name;
            const paramValue = checkbox.value;

            checkbox.checked = urlParams.getAll(paramName).includes(paramValue);
        });
    }
    updateCheckboxStates();
});