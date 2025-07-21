from typing import List, Literal, Union


QueryFilter = Literal["$eq", "$ne", "$gt", "$lt", "$gte", "$lte", "$in", "$nin", "$regex"]

ValueFilter = Union[str, int, float, List[str], List[int], List[float]]

FilterType = dict[QueryFilter, ValueFilter]

FilterParameter = dict[str, FilterType]