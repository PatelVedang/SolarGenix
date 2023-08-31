from django.core.cache import cache
import json
import pandas as pd
import time


# The `Cache` class provides methods for interacting with a cache, including getting, setting,
# updating, filtering, and deleting cache entries.
class Cache:

    @classmethod
    def get(cls, key):
        """
        The function `get` retrieves a value from a cache using a key and returns it as a JSON object.
        
        :param cls: The parameter "cls" is typically used as a reference to the class itself. It is
        commonly used in class methods to access class-level attributes or methods. In this case, it
        seems that the "get" method is a class method, and "cls" is being used to refer to the class
        :param key: The key parameter is a string that represents the key used to retrieve data from the
        cache
        :return: a JSON object that is obtained from the cache using the provided key. If the key is not
        found in the cache, an empty JSON object is returned.
        """
        return json.loads(cache.get(key, '{}'))
    
    @classmethod
    def has_key(cls, key):
        return cache.has_key(key)
    
    @classmethod
    def set(cls, key, **kwargs):
        """
        The function sets a value in the cache using a key and keyword arguments.
        
        :param cls: The parameter `cls` is typically used as a reference to the class itself. It is
        commonly used in class methods to access class-level attributes or methods. In this case, it
        seems that `cls` is not being used in the method, so it may not be necessary
        :param key: The key parameter is a unique identifier for the data being stored in the cache. It
        is used to retrieve the data later when needed
        """
        print(f"Cache set for key : {key}")
        cache.set(key, json.dumps(kwargs, default=str))

    @classmethod
    def update(cls, key, **kwargs):
        """
        The function updates a JSON object stored in a cache with new key-value pairs.
        
        :param cls: The parameter `cls` is typically used as a reference to the class itself. It is
        commonly used in class methods to access class-level attributes or methods. In this case, it
        seems that the `update` method is defined within a class, and `cls` is used as a reference to
        that
        :param key: The `key` parameter is a unique identifier for the data that you want to update in
        the cache. It is used to retrieve the existing data from the cache and update it with the new
        values provided in the `kwargs` parameter
        """
        # Update take only json
        counter = 0
        while counter!=4:
            if cache.has_key(key):
                break
            counter += 1
            time.sleep(1)
            
        if cache.has_key(key):
            cache.set(key, json.dumps(
                {**json.loads(cache.get(key)), **kwargs}, default=str))
            print(f"Cache update successfully with key {key} =>>>>>>>>>>>>>>")
        else:
            print(f"Cache not found with key {key} =>>>>>>>>>>>>>>")

    # @classmethod
    # def apply_filter(cls, records, conditions):
    #     """
    #     The function `apply_filter` takes a list of records and a list of conditions, and returns a
    #     filtered list of records that meet all the conditions.
        
    #     :param cls: The parameter `cls` is not used in the function and can be removed
    #     :param records: The `records` parameter is a list of dictionaries. Each dictionary represents a
    #     record with various fields and their corresponding values
    #     :param conditions: The `conditions` parameter is a list of tuples, where each tuple represents a
    #     condition to be applied to the records. Each tuple has three elements:
    #     :return: a list of filtered records that meet all the conditions specified.
    #     """
    #     filtered_records = []
    #     for record in records:
    #         all_conditions_met = True
    #         for condition in conditions:
    #             if len(condition) == 3:
    #                 field, op, match_value = condition
    #                 if op == 'in' and not isinstance(record.get(field),type(None)) and record.get(field) not in match_value:
    #                     all_conditions_met = False
    #                     break
    #                 elif op == 'eq' and not isinstance(record.get(field),type(None)) and record.get(field) != match_value:
    #                     all_conditions_met = False
    #                     break
    #                 elif op == 'lt' and not isinstance(record.get(field),type(None)) and record.get(field) >= match_value:
    #                     all_conditions_met = False
    #                     break
    #                 elif op == 'gt' and not isinstance(record.get(field),type(None)) and record.get(field) <= match_value:
    #                     all_conditions_met = False
    #                     break
    #                 elif op == 'lte' and not isinstance(record.get(field),type(None)) and record.get(field) > match_value:
    #                     all_conditions_met = False
    #                     break
    #                 elif op == 'gte' and not isinstance(record.get(field),type(None)) and record.get(field) < match_value:
    #                     all_conditions_met = False
    #                     break
    #                 elif op == 'nq' and not isinstance(record.get(field),type(None)) and record.get(field) == match_value:
    #                     all_conditions_met = False
    #                     break

    #         if all_conditions_met:
    #             filtered_records.append(record)

    #     return filtered_records
    
    @classmethod
    def apply_filter(cls,records, conditions):
        """
        The function `apply_filter` takes a list of records, applies a set of conditions to filter the
        records, and returns the filtered records as a list of dictionaries.
        
        :param cls: The parameter "cls" is not used in the function and can be removed
        :param records: The "records" parameter is a list of dictionaries, where each dictionary
        represents a record or row of data. Each dictionary should have the same keys, which represent
        the field names, and the corresponding values represent the data for each field
        :param conditions: The `conditions` parameter is a list of lists, where each inner list
        represents a condition to filter the records. Each inner list should have three elements:
        :return: a list of filtered records that match the given conditions.
        """
        df = pd.DataFrame(records)
        for condition in conditions:
            if isinstance(condition,list) and len(condition) == 3:
                field, op, match_value = condition
                if field in df.columns:
                    if op == 'in':
                        df = df[df[field].isin(match_value)]
                    elif op == 'eq':
                        df = df[df[field] == match_value]
                    elif op == 'lt':
                        df = df[df[field] < match_value]
                    elif op == 'gt':
                        df = df[df[field] > match_value]
                    elif op == 'lte':
                        df = df[df[field] <= match_value]
                    elif op == 'gte':
                        df = df[df[field] >= match_value]
                    elif op == 'nq':
                        df = df[df[field] != match_value]
        
        filtered_records = df.to_dict(orient='records')
        return filtered_records

    @classmethod
    def delete(cls, key):
        """
        The function deletes a key from a cache if it exists.
        
        :param cls: The parameter "cls" is typically used as a convention to refer to the class itself
        within a class method. It is similar to the "self" parameter used in instance methods, but "cls"
        is used to refer to the class object itself rather than an instance of the class
        :param key: The key parameter is the unique identifier for the data that you want to delete from
        the cache
        """
        if cache.has_key(key):
            cache.delete(key)
    
    @classmethod
    def delete_many(cls, keys=[]):
        """
        The function `delete_many` deletes multiple keys from a cache.
        
        :param cls: The parameter "cls" is typically used as a reference to the class itself. It is
        commonly used in class methods to access class-level attributes or methods. In this case, it
        seems that "cls" is being used as a reference to the class that contains this method
        :param keys: The `keys` parameter is a list of keys that you want to delete from the cache. Each
        key represents a specific item or data stored in the cache
        """
        cache.delete_many(keys)

    @classmethod
    def get_order_targets(cls, key):
        """
        The function `get_order_targets` retrieves a list of target objects based on a given key.
        
        :param cls: The parameter `cls` is a reference to the class that this method belongs to. It is
        used to call the `get_many` method on the class
        :param key: The `key` parameter is a string that represents the key used to retrieve the order
        object from the cache
        :return: the result of `cls.get_many(targets_ids)`.
        """
        order_obj = json.loads(cache.get(key,'{}'))
        targets_ids = [f'target_{target["id"]}' for target in order_obj.get('targets',[])]
        return cls.get_many(targets_ids)
        # targets_list =[]
        # if order_obj:
        #     targets = order_obj.get('targets',[])
        #     for target in targets :
        #         target_obj = json.loads(cache.get(f'target_{target["id"]}','{}'))
        #         targets_list.append(target_obj)
        # return targets_list

    @classmethod
    def get_many(cls, keys):
        """
        The function `get_many` takes a class and a list of keys, retrieves the corresponding values
        from a cache, and returns them as a list of JSON objects.
        
        :param cls: The parameter `cls` is a reference to a class. It is used to specify the class that
        the returned objects should be instances of
        :param keys: The `keys` parameter is a list of keys that you want to retrieve from the cache
        :return: A list of JSON objects is being returned.
        """
        return [json.loads(target) for target in list(cache.get_many(keys).values())]

