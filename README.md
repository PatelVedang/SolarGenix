# Django Custom Filter Function

## Overview
The `filter_model` function is a utility designed to filter a Django `QuerySet` based on dynamic query parameters provided through a `QueryDict` (typically from a Django request object). It allows for flexible filtering, sorting, and selection of specific fields from a queryset in a highly customizable manner.

## Table of Contents
- [Function Signature](#function-signature)
- [Arguments](#arguments)
- [Return Value](#return-value)
- [Supported Query Parameters](#supported-query-parameters)
  - [1. `search_fields`](#1-search_fields)
  - [2. `search`](#2-search)
  - [3. `sort`](#3-sort)
  - [4. `select`](#4-select)
  - [5. Filtering by Fields](#5-filtering-by-fields)
- [Supported Django Filter Queries](#supported-django-filter-queries)
  - [Exact match (`__exact`)](#exact-match-__exact)
  - [Case-insensitive exact match (`__iexact`)](#case-insensitive-exact-match-__iexact)
  - [Contains (`__contains`)](#contains-__contains)
  - [Case-insensitive contains (`__icontains`)](#case-insensitive-contains-__icontains)
  - [Greater than (`__gt`)](#greater-than-__gt)
  - [Greater than or equal (`__gte`)](#greater-than-or-equal-__gte)
  - [Less than (`__lt`)](#less-than-__lt)
  - [Less than or equal (`__lte`)](#less-than-or-equal-__lte)
  - [In a list (`__in`)](#in-a-list-__in)
  - [Not in a list (`__not_in`) (custom)](#not-in-a-list-__not_in-custom)
  - [ForeignKey related filtering (`__foreignkey__id`)](#foreignkey-related-filtering-__foreignkey__id)
- [Usage Examples](#usage-examples)
  - [Example 1: Search and Filter](#example-1-search-and-filter)
  - [Example 2: Sort and Select](#example-2-sort-and-select)
  - [Example 3: Complex Filtering with ForeignKey](#example-3-complex-filtering-with-foreignkey)
  - [Example 4: Exclude Using `not_in`](#example-4-exclude-using-not_in)
- [.gitignore](#gitignore)
- [Notes](#notes)

## Function Signature
```python
def filter_model(
    query_params: QueryDict, queryset: QuerySet[Model], model: Type[Model]
) -> QuerySet[Model]:
    """
    Filter the given queryset based on the provided query parameters.

    Args:
        query_params (QueryDict): A QueryDict containing the query parameters.
        queryset (QuerySet[Model]): The queryset to be filtered.
        model (Type[Model]): The model class.

    Returns:
        QuerySet[Model]: The filtered queryset.
    """
```

## Arguments

- **query_params (`QueryDict`)**:  
  A `QueryDict` object that contains the filtering, sorting, and field selection parameters. Typically, this comes from `request.GET` or `request.POST` in Django views.
  
- **queryset (`QuerySet[Model]`)**:  
  The `QuerySet` to be filtered. This should be pre-fetched from the database, and the function will apply filtering conditions based on `query_params`.
  
- **model (`Type[Model]`)**:  
  The model class on which the filtering is based. This is used to inspect the model’s fields dynamically and apply the appropriate filtering logic.

## Return Value

- **`QuerySet[Model]`**:  
  The filtered `QuerySet`, potentially sorted and limited by the selected fields.

## Supported Query Parameters

### 1. `search_fields`
- **Description**: Comma-separated list of fields to apply search against.
- **Example**:  
  `/api/products/?search_fields=name,description`
- **Default**: All fields of the model that are non-relational (`Field`) if `search_fields` is not provided.
- **Details**: If `search_fields` is specified, the search will only apply within those fields.

### 2. `search`
- **Description**: Applies a case-insensitive search across the specified fields or all fields of the model if `search_fields` is not provided.
- **Example**:  
  `/api/products/?search=shoes&search_fields=name,description`
- **Details**: The function creates an `OR` condition for each field to match the search string, such as `name__icontains="shoes"` and `description__icontains="shoes"`.

### 3. `sort`
- **Description**: Comma-separated list of fields by which to sort the results. Supports ascending and descending ordering.
- **Example (Ascending)**:  
  `/api/products/?sort=name,price`
- **Example (Descending)**:  
  `/api/products/?sort=-price`
- **Details**: The function sorts the `QuerySet` based on the provided fields.

### 4. `select`
- **Description**: Comma-separated list of fields to return in the query. Limits the selected fields, useful for reducing the amount of data retrieved from the database.
- **Example**:  
  `/api/products/?select=name,price`
- **Default**: The primary key (`id`) will always be included in the selected fields, even if not explicitly specified.

### 5. Filtering by Fields
- **Description**: Supports Django-style lookup expressions for filtering fields.
- **Example**:  
  `/api/products/?price__gte=100&category__id__in=1,2,3`  
  `/api/products/?created_at__lte=2023-01-01`
- **Details**: Filters are applied dynamically based on the query string.

---

## Supported Django Filter Queries

The function supports all standard Django lookups such as:

1. **Exact match (`__exact`)**: 
   - **Usage:** `field=value`
   - **Example:** `/api/products/?name__exact=Nike`

2. **Case-insensitive exact match (`__iexact`)**: 
   - **Usage:** `field__iexact=value`
   - **Example:** `/api/products/?name__iexact=nike`

3. **Contains (`__contains`)**: 
   - **Usage:** `field__contains=value`
   - **Example:** `/api/products/?description__contains=sport`

4. **Case-insensitive contains (`__icontains`)**: 
   - **Usage:** `field__icontains=value`
   - **Example:** `/api/products/?name__icontains=nike`

5. **Starts with (`__startswith`)**: 
   - **Usage:** `field__startswith=value`
   - **Example:** `/api/products/?name__startswith=Ni`

6. **Case-insensitive starts with (`__istartswith`)**: 
   - **Usage:** `field__istartswith=value`
   - **Example:** `/api/products/?name__istartswith=ni`

7. **Ends with (`__endswith`)**: 
   - **Usage:** `field__endswith=value`
   - **Example:** `/api/products/?name__endswith=ke`

8. **Case-insensitive ends with (`__iendswith`)**: 
   - **Usage:** `field__iendswith=value`
   - **Example:** `/api/products/?name__iendswith=ke`

9. **Greater than (`__gt`)**: 
   - **Usage:** `field__gt=value`
   - **Example:** `/api/products/?price__gt=100`

10. **Greater than or equal (`__gte`)**: 
    - **Usage:** `field__gte=value`
    - **Example:** `/api/products/?price__gte=100`

11. **Less than (`__lt`)**: 
    - **Usage:** `field__lt=value`
    - **Example:** `/api/products/?price__lt=200`

12. **Less than or equal (`__lte`)**: 
    - **Usage:** `field__lte=value`
    - **Example:** `/api/products/?price__lte=200`

13. **In a list (`__in`)**: 
    - **Usage:** `field__in=value1,value2,value3`
    - **Example:** `/api/products/?category__id__in=1,2,3`

14. **Not in a list (`__not_in`)** (custom): 
    - **Usage:** `field__not_in=value1,value2,value3`
    - **Example:** `/api/products/?category__id__not_in=1,2,3`
    - **Details:** This will filter out all records where `category__id` is 1, 2, or 3.

15. **Is null (`__isnull`)**: 
    - **Usage:** `field__isnull=True/False`
    - **Example:** `/api/products/?description__isnull=True`

16. **Regular expression match (`__regex`)**: 
    - **Usage:** `field__regex=value`
    - **Example:** `/api/products/?name__regex=^Ni.*ke$`
    - **Details:** This matches using regular expressions.

17. **Case-insensitive regular expression match (`__iregex`)**: 
    - **Usage:** `field__iregex=value`
    - **Example:** `/api/products/?name__iregex=^ni.*ke$`
    - **Details:** This matches using case-insensitive regular expressions.

18. **ForeignKey related filtering (`__foreignkey__id`)**: 
    - **Usage:** `related_field__id=value`
    - **Example:** `/api/products/?category__id=1`

19. **Range (`__range`)**: 
    - **Usage:** `field__range=(start, end)`
    - **Example:** `/api/products/?price__range=100,200`

20. **Year (`__year`)**: 
    - **Usage:** `field__year=value`
    - **Example:** `/api/products/?created_at__year=2023`

21. **Month (`__month`)**: 
    - **Usage:** `field__month=value`
    - **Example:** `/api/products/?created_at__month=9`

22. **Day (`__day`)**: 
    - **Usage:** `field__day=value`
    - **Example:** `/api/products/?created_at__day=15`

23. **Weekday (`__week_day`)**: 
    - **Usage:** `field__week_day=value`
    - **Example:** `/api/products/?created_at__week_day=2` (Monday=2)

24. **Time (`__time`)**: 
    - **Usage:** `field__time=value`
    - **Example:** `/api/products/?created_at__time=12:00:00`

---

## Usage Examples

### Example 1: Search and Filter
```
GET /api/products/?search=nike&search_fields=name,description&price__gte=100&category__id__in=1,2
```
- **Action**: Searches for products with "nike" in the name or description, where the price is greater than or equal to 100, and the category ID is in 1 or 2.

### Example 2: Sort and Select
```
GET /api/products/?sort=-price,name&select=name,price,category__name
```
- **Action**: Selects only the `name`, `price`, and `category__name` fields, sorts by price descending, and then by name ascending.

### Example 3: Complex Filtering with ForeignKey
```
GET /api/orders/?status=completed&customer__id=5&order_date__lte=2023-01-01
```
- **Action**: Filters orders with status "completed", related customer ID equal to 5, and order date less than or equal to January 1, 2023.

### Example 4: Exclude Using `not_in`
```
GET /api/products/?category__id__not_in=3,4,5
```
- **Action**: Excludes products where `category__id` is 3, 4, or 5.

## .gitignore
```.gitignore
**/scripts/
.cz.toml
setup.ps1
.pre-commit-config.yaml
```
- **Note**: Before pushing code to production(before first commit and push to origin), ensure that all non-essential files and directories (such as scripts/) are properly listed in the .gitignore file to prevent them from being included in the production environment.

## Notes

- **Nested Lookups**: The function handles nested lookups, such as `related_field__field_name__gte`, dynamically. This is useful for filtering based on related models.
- **

List Parsing**: Values for lookups like `in` and `not_in` are split by commas and parsed into a list automatically.
- **Literal Evaluation**: The function uses `literal_eval` to convert string representations of lists or complex objects (e.g., JSON-like structures) into actual Python types.
