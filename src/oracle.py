
class Oracle:
    def membership_query(self, string):
        raise NotImplementedError("Oracle must implement membership_query()")
    
    def equivalence_query(self, dfa):
        raise NotImplementedError("Oracle must implement equivalence_query()")
