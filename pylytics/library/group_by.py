"""
A class to implement simple group by functionality in Python.

"""
from collections import defaultdict


def clean_values(sequence):
    """Remove all None values from the sequence."""
    cleaned_sequence = [value for value in sequence if value != None]
    if not cleaned_sequence:
        # Some functions might struggle getting an empty list.
        cleaned_sequence = [0]
    return cleaned_sequence


class GroupBy(object):
    def __init__(self, data_input, group_by, cols=None, dims=[]):
        """
        data_input is the result of a SQL select query.
        
        group_by is a dictionary, e.g.:
        
        > group_by = {
        >     'indexes': [0, 6], # The columns to group_by.
        >     'functions': {
        >         'sum': [2, 3, 4],
        >     },
        > }
        
        indexes is required, and at least one function.
        
        """
        self.data_input = data_input
        self.col_id = {i:i for i in range(len(data_input[0]))} if cols is None else {name:i for i,name in enumerate(cols)}
        self.indexes = [self.col_id[e] for e in group_by['by']]
        self.functions = self._get_updated_functions(group_by['functions'])
        self.functions_corresp = {self.col_id[e]:self.functions[k] for k,l in group_by['aggregate'].items() for e in l}
        self.dims = [self.col_id[e] for e in dims]
        self.data_output = []
        self.groups = defaultdict(list)
        self.cols = cols
    
    def _group_input_data(self):
        for row in self.data_input:
            self.groups[tuple(row[i] for i in self.indexes)].append(row)
    
    def count_distinct(self, values):
        return len(set(values))
    
    def _get_updated_functions(self, user_def_functions):
        functions_dict = {
            'sum' : sum,
            'avg': lambda x : float(sum(x))/float(len(x)),
            'count': len,
            'count_distinct': lambda x : len(set(x))           
        }
        functions_dict.update(user_def_functions)
        return functions_dict
    
    def _create_output(self):
        for key,group in self.groups.items():
            output_row = []
            
            for col,values in enumerate(zip(*group)):
                cleaned_values = clean_values(values)
                if col in self.indexes or col in self.dims:
                    output_row.append(cleaned_values[0])
                elif col in self.functions_corresp:
                    output_row.append(self.functions_corresp[col](cleaned_values))
            
            self.data_output.append(output_row)
    
    def process(self):
        self._group_input_data()
        self._create_output()
        import pdb; pdb.set_trace()
        return self.data_output
