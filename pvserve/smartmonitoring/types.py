from dataclasses import dataclass

@dataclass
class Plant:
    pv_strings:List[PVString]

@dataclass
class PVString:
    num_parallel:int
    num_serie:int
    manufacturer:str
    modul_typ:str
    isc:float
    voc:float
    bright_curves:List[BrightCurve]
    dark_curve:List[DarkCurve]

@dataclass
class BrightCurve:
    curve:List[IVPair]

@dataclass
class DarkCurve:
    curve:List[IVPair]

@dataclass
class IVPair:
    i:float
    v:float