from typing import Optional
from datetime import datetime, timedelta


class SessionHelper:

    @classmethod
    def contains_point(
        cls, 
        p: datetime, 
        x: datetime, 
        y: Optional[datetime] = None,
    ) -> bool: 
        if y is not None: 
            return p >= x and p <= y
        
        return p > x
    
    @classmethod
    def contains_interval(
        cls,
        s1_b: Optional[datetime] = None,
        s1_e: Optional[datetime] = None,
        s2_b: Optional[datetime] = None,
        s2_e: Optional[datetime] = None,
    ) -> bool:
        """Проверка вхождения одной сесии в другую"""
        if s1_b is None or s2_b is None:
            return False

        x1 = s1_b.timestamp()
        x2 = (
            s1_e.timestamp()
            if s1_e is not None
            else (s1_b + timedelta(days=365)).timestamp()
        )
        y1 = s2_b.timestamp()
        y2 = (
            s2_e.timestamp()
            if s2_e is not None
            else (s2_b + timedelta(days=365)).timestamp()
        )

        return (x1 - y2) * (x2 - y1) > 0


__all__ = ["SessionHelper"]
