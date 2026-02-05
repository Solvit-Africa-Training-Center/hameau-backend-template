from rest_framework import filters

class CustomSearchFilter(filters.SearchFilter):
    search_param = 'search'
    
    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        params = params.replace(',', ' ')
        return params.split()
