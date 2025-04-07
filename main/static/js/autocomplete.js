// main/static/js/autocomplete.js
document.addEventListener('DOMContentLoaded', function() {
    const searchBars = document.querySelectorAll('.search-bar');
    
    searchBars.forEach(searchBar => {
        searchBar.addEventListener('input', function() {
            let query = this.value;
            console.log('Fetching suggestions for query:', query);
            fetch(`/users/autocomplete/?q=${query}`)
                .then(response => {
                    console.log('Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Suggestions received:', data);
                    let suggestionsDiv = searchBar.closest('form').querySelector('.suggestions');
                    if (suggestionsDiv) {
                        suggestionsDiv.innerHTML = '';
                        data.suggestions.forEach(suggestion => {
                            let div = document.createElement('div');
                            div.style.padding = '5px';
                            div.style.cursor = 'pointer';
                            div.style.borderBottom = '1px solid #eee';
                            div.innerHTML = `
                                <div style="font-weight: bold;">${suggestion.title}</div>
                                <div style="font-size: 12px; color: #666;">${suggestion.instructor}</div>
                            `;
                            div.addEventListener('click', () => {
                                searchBar.value = suggestion.title;
                                suggestionsDiv.innerHTML = '';
                                searchBar.closest('form').submit();
                            });
                            suggestionsDiv.appendChild(div);
                        });
                    } else {
                        console.error('Suggestions div not found');
                    }
                })
                .catch(error => console.error('Error fetching suggestions:', error));
        });
    });
});