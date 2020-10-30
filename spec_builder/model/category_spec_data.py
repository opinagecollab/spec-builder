

class CategorySpecData:

    def __init__(self, **kwargs):
        if 'category_id' in kwargs:
            self.category_id = kwargs.get('category_id')
            self.parent_category_id = None
        else:
            self.category_id = None
            self.parent_category_id = kwargs.get('parent_category_id')

        self.spec_id = kwargs.get('spec_id')
        self.directly_activated = kwargs.get('directly_activated')
        self.directly_not_activated = kwargs.get('directly_not_activated')
        self.children_activated = kwargs.get('children_activated')
        self.children_not_activated = kwargs.get('children_not_activated')

