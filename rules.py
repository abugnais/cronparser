
import re
from typing import List
from abc import ABC, abstractmethod

class BaseRule(ABC):
    @abstractmethod
    def match(self, expression:str) -> bool:
        pass

    @abstractmethod
    def parse(self, expression:str, values:List[int]) -> List[int]:
        pass

class StepRule(BaseRule):
    regex = '^(\d*|\*)\/\d*$'

    def match(self, expression:str) -> bool:
        return re.match(self.regex, expression) != None

    def parse(self, expression:str, values:List[int]) -> List[int]:
        params = expression.split('/')
        base = params[0]
        step = int(params[1])

        if base == '*':
            base = 0
        else:
            base = int(base)

        if step > values[-1]:
            raise RuntimeError('invalid expression, the step cannot be larger than the maximum value {}'.format(step))
        if step == 0:
            raise RuntimeError('invalid expression, the step cannot be zero')
        return [val for val in range(base, values[-1], step)]

class ListRule(BaseRule):
    regex = '^\d+(,\d+)+$'

    def match(self, expression:str) -> bool:
        return re.match(self.regex, expression) != None

    def parse(self, expression:str, values:List[int]) -> List[int]:
        params = [int(param) for param in expression.split(',')]
        for param in params:
            if param not in values:
                raise RuntimeError('invalid list values')
        return sorted(params)

class WildCardRule(BaseRule):
    def match(self, expression:str) -> bool:
        return expression == '*'

    def parse(self, expression:str, values:List[int]) -> List[int]:
        return values

class LiteralRule(BaseRule):
    regex = '^\d*$'

    def match(self, expression:str) -> bool:
        return re.match(self.regex, expression) != None

    def parse(self, expression:str, values:List[int]) -> List[int]:
        value = int(expression)
        if  value not in values:
            raise RuntimeError("invalid value {} not included in {}".format(str(value), values))
        return [value]

class RangeRule(BaseRule):
    regex = '^\d*\-\d*(\/\d*)?$'

    def match(self, expression:str) -> bool:
        return re.match(self.regex, expression) != None

    def parse(self, expression:str, values:List[int]) -> List[int]:
        params = re.compile('[\-\/]').split(expression)
        start = int(params[0])
        end = int(params[1])
        step = int(params[2]) if len(params) == 3 else 1

        if step > values[-1]:
            raise RuntimeError('invalid expression, the step cannot be larger than the maximum value {}'.format(step))
        if step == 0:
            raise RuntimeError('invalid expression, the step cannot be zero')
        if start > end:
            raise RuntimeError('invalid expression beginning of the range {} is greater than the end of the range {}'.format(start, end))
        if start < values[0]:
            raise RuntimeError('invalid expression beginning of the range {} is less than the minimum allowed value {}'.format(start, values[0]))
        if end > values[-1]:
            raise RuntimeError('invalid expression end of the range {} is greater than the maximum allowed value {}'.format(end, values[-1]))
        return [v for v in range(start, end + 1, step)]

class DefaultRule(BaseRule):
    def match(self, expression):
        raise RuntimeError('none of the rules were matched for expression {}'.format(expression))

    def parse(self, expression:str, values:List[int]) -> List[int]:
        raise RuntimeError('none of the rules were matched for expression {}'.format(expression))