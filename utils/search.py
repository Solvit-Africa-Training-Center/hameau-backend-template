from rest_framework import filters

class CustomSearchFilter(filters.SearchFilter):
    """
    Custom search filter to standardize search functionality options.
    """
    search_param = 'search'
    
    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace(',', ' ')
        return params.split()
