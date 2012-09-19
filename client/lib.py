class JSDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)



if __name__ == '__main__':
    d = JSDict({'hello': 1})
    print d.hello # => 1




    




