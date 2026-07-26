"""Focused verification for the custom gag-experience multiplier rules.

Run this with the project's bundled ``ppython`` from the game directory.  The
test executes the production multiplier methods directly from their AST while
avoiding the cost of starting a complete AI district.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys


GAME_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME_ROOT))

from toontown.toonbase.ToontownBattleGlobals import (  # noqa: E402
    getBaseGagExperienceMultiplier,
    getBuildingGagExperienceMultiplier,
    getCreditMultiplier,
    getInvasionMultiplier,
    getMoreXpHolidayMultiplier,
)


class _Toggle:
    def __init__(self, enabled: bool, method_name: str) -> None:
        self.enabled = enabled
        self.calls = 0
        setattr(self, method_name, self._read)

    def _read(self) -> bool:
        self.calls += 1
        return self.enabled


class _Air:
    def __init__(self, invasion: bool, more_xp: bool) -> None:
        self.suitInvasionManager = _Toggle(invasion, "getInvading")
        self.holidayManager = _Toggle(
            more_xp, "isMoreXpHolidayRunning"
        )


class _Simbase:
    def __init__(self) -> None:
        self.air = _Air(False, False)


simbase = _Simbase()


def _load_production_multiplier_methods():
    source_path = GAME_ROOT / "toontown" / "battle" / "BattleCalculatorAI.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"), source_path)
    source_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "BattleCalculatorAI"
    )
    wanted = {
        "setSkillCreditMultiplier",
        "setSkillCreditMultiplierAbsolute",
        "__getGlobalSkillCreditMultiplier",
        "getSkillCreditMultiplier",
    }
    methods = [
        node
        for node in source_class.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    if {method.name for method in methods} != wanted:
        raise AssertionError("Could not find every production multiplier method")
    test_class = ast.ClassDef(
        name="BattleCalculatorUnderTest",
        bases=[],
        keywords=[],
        body=methods,
        decorator_list=[],
    )
    module = ast.Module(body=[test_class], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "simbase": simbase,
        "getBaseGagExperienceMultiplier": getBaseGagExperienceMultiplier,
        "getInvasionMultiplier": getInvasionMultiplier,
        "getMoreXpHolidayMultiplier": getMoreXpHolidayMultiplier,
    }
    exec(compile(module, source_path, "exec"), namespace)
    return namespace["BattleCalculatorUnderTest"]


def _assert_multiplier(
    calculator_type,
    label: str,
    expected: float,
    *,
    local_multiplier: float = 1,
    absolute: bool = False,
    invasion: bool = False,
    more_xp: bool = False,
) -> None:
    simbase.air = _Air(invasion, more_xp)
    calculator = calculator_type()
    if absolute:
        calculator.setSkillCreditMultiplierAbsolute(local_multiplier)
    else:
        calculator.setSkillCreditMultiplier(local_multiplier)
    actual = calculator.getSkillCreditMultiplier()
    if actual != expected:
        raise AssertionError(
            f"{label}: expected {expected:g}x, got {actual:g}x"
        )
    if simbase.air.suitInvasionManager.calls != 1:
        raise AssertionError(f"{label}: invasion bonus was not checked once")
    if simbase.air.holidayManager.calls != 1:
        raise AssertionError(f"{label}: More-XP bonus was not checked once")
    print(f"PASS {label}: {actual:g}x")


def _assert_wiring() -> None:
    normal_ai = (
        GAME_ROOT / "toontown" / "building" / "DistributedSuitInteriorAI.py"
    ).read_text(encoding="utf-8")
    normal_client = (
        GAME_ROOT / "toontown" / "building" / "DistributedSuitInterior.py"
    ).read_text(encoding="utf-8")
    cogdo_ai = (
        GAME_ROOT
        / "toontown"
        / "cogdominium"
        / "DistributedCogdoInteriorAI.py"
    ).read_text(encoding="utf-8")

    required_normal_ai = (
        "getBuildingGagExperienceMultiplier(self.numFloors)",
        "setSkillCreditMultiplierAbsolute(mult)",
    )
    required_normal_client = (
        "getBuildingGagExperienceMultiplier(self.numFloors)",
        "setBattleCreditMultiplier(mult, absolute=True)",
    )
    for snippet in required_normal_ai:
        if snippet not in normal_ai:
            raise AssertionError(f"Normal-building AI wiring missing: {snippet}")
    for snippet in required_normal_client:
        if snippet not in normal_client:
            raise AssertionError(
                f"Normal-building client wiring missing: {snippet}"
            )

    cogdo_tree = ast.parse(cogdo_ai)
    create_battle = next(
        node
        for node in ast.walk(cogdo_tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "__createFloorBattle"
    )
    called_names = {
        node.func.id
        for node in ast.walk(create_battle)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    if "getCreditMultiplier" not in called_names:
        raise AssertionError("Cogdo floor multiplier is not wired")
    if "getInvasionMultiplier" in called_names:
        raise AssertionError("Cogdo applies the invasion multiplier twice")
    if "setSkillCreditMultiplier(mult)" not in cogdo_ai:
        raise AssertionError("Cogdo does not stack its floor multiplier")
    print("PASS server/client wiring and single-application Cogdo audit")


def main() -> None:
    calculator_type = _load_production_multiplier_methods()
    base = getBaseGagExperienceMultiplier()
    building_three = getBuildingGagExperienceMultiplier(3)
    invasion = getInvasionMultiplier()
    holiday = getMoreXpHolidayMultiplier()

    _assert_multiplier(calculator_type, "street battle", base)
    _assert_multiplier(
        calculator_type,
        "street + invasion + More-XP",
        base * invasion * holiday,
        invasion=True,
        more_xp=True,
    )
    _assert_multiplier(
        calculator_type,
        "three-story building",
        building_three,
        local_multiplier=building_three,
        absolute=True,
    )
    _assert_multiplier(
        calculator_type,
        "three-story building + invasion + More-XP",
        building_three * invasion * holiday,
        local_multiplier=building_three,
        absolute=True,
        invasion=True,
        more_xp=True,
    )
    third_cogdo_floor = getCreditMultiplier(2)
    _assert_multiplier(
        calculator_type,
        "third Cogdo floor + invasion + More-XP",
        base * third_cogdo_floor * invasion * holiday,
        local_multiplier=third_cogdo_floor,
        invasion=True,
        more_xp=True,
    )
    _assert_wiring()


if __name__ == "__main__":
    main()
