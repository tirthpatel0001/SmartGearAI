"""
app/final.py

Provides a small bridge to load and run predictions from:
- quality_defect_ui.py
- gear_detection.py

This file attempts to import the modules from common locations and
exposes simple functions to load models and run predictions in a
safe, flexible manner.
"""
from importlib import import_module
from typing import Any, Callable, Optional, Tuple, List
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _import_first_available(module_names: List[str]):
    for name in module_names:
        try:
            mod = import_module(name)
            logger.info("Imported module: %s", name)
            return mod
        except Exception:
            continue
    raise ImportError(f"None of the modules could be imported: {module_names}")


def _find_callable(module: Any, candidates: List[str]) -> Optional[Callable]:
    for name in candidates:
        fn = getattr(module, name, None)
        if callable(fn):
            return fn
    return None


class ModelBridge:
    """
    Bridge to load and call functions from the quality and gear detection modules.

    Usage:
      bridge = ModelBridge()
      quality_model = bridge.load_quality_model(path_or_args)
      result = bridge.predict_quality(input_path, quality_model)

      gear_model = bridge.load_gear_model(path_or_args)
      gear_result = bridge.predict_gear(input_path, gear_model)
    """

    def __init__(self):
        # Try importing quality module from several typical locations
        self.quality_module = None
        self.gear_module = None

        quality_candidates = [
            "app.quality_defect_ui",
            "quality_defect_ui",
            "src.quality_defect.quality_defect_ui",
            "src.quality_defect.predict_quality",
        ]
        gear_candidates = [
            "app.gear_detection",
            "gear_detection",
            "src.gear_detection",
            "src.gear_box_defect.predict",
        ]

        try:
            self.quality_module = _import_first_available(quality_candidates)
        except ImportError as e:
            logger.warning("Quality module not found: %s", e)

        try:
            self.gear_module = _import_first_available(gear_candidates)
        except ImportError as e:
            logger.warning("Gear module not found: %s", e)

    # -------- Quality model helpers --------
    def load_quality_model(self, *args, **kwargs) -> Any:
        """
        Load the quality model. Tries common loader function names.
        Returns the loaded model object or raises RuntimeError.
        """
        if not self.quality_module:
            raise RuntimeError("Quality module not available")

        loader = _find_callable(self.quality_module, ["load_quality_model", "load_model", "get_model"])
        if not loader:
            raise RuntimeError("No loader function found in quality module")

        return loader(*args, **kwargs)

    def predict_quality(self, input_path: str, model: Any = None, *args, **kwargs) -> Any:
        """
        Predict quality for input_path using the provided model or by letting
        the underlying module handle model management if its predict function
        expects only the path.
        """
        if not self.quality_module:
            raise RuntimeError("Quality module not available")

        predictor = _find_callable(self.quality_module, ["predict_quality", "predict", "detect"])
        if not predictor:
            raise RuntimeError("No predictor function found in quality module")

        # Try calling predictor with (input_path, model) then fallback to (input_path)
        try:
            if model is not None:
                return predictor(input_path, model, *args, **kwargs)
            return predictor(input_path, *args, **kwargs)
        except TypeError:
            # fallback: try without model
            return predictor(input_path)

    # -------- Gear model helpers --------
    def load_gear_model(self, *args, **kwargs) -> Any:
        """
        Load the gear detection/diagnosis model. Tries common loader function names.
        """
        if not self.gear_module:
            raise RuntimeError("Gear module not available")

        loader = _find_callable(self.gear_module, ["load_gear_model", "load_model", "get_model"])
        if not loader:
            raise RuntimeError("No loader function found in gear module")

        return loader(*args, **kwargs)

    def predict_gear(self, input_path: str, model: Any = None, *args, **kwargs) -> Any:
        """
        Run gear detection/prediction on input_path.
        """
        if not self.gear_module:
            raise RuntimeError("Gear module not available")

        predictor = _find_callable(
            self.gear_module,
            ["predict_fault_and_severity", "predict", "detect", "predict_gear"]
        )
        if not predictor:
            raise RuntimeError("No predictor function found in gear module")

        try:
            if model is not None:
                return predictor(input_path, model, *args, **kwargs)
            return predictor(input_path, *args, **kwargs)
        except TypeError:
            return predictor(input_path)


# Simple CLI to allow quick access when executed directly
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Access quality and gear detection models")
    parser.add_argument("--type", choices=["quality", "gear"], required=True, help="Which model to use")
    parser.add_argument("--input", required=True, help="Input file path (image or csv)")
    parser.add_argument("--load-arg", help="Optional argument passed to loader (e.g. model path)", default=None)
    args = parser.parse_args()

    bridge = ModelBridge()

    try:
        if args.type == "quality":
            model = None
            try:
                if args.load_arg:
                    model = bridge.load_quality_model(args.load_arg)
                else:
                    model = bridge.load_quality_model()
            except Exception as e:
                logger.info("Quality model loader not usable (%s). Proceeding without explicit model.", e)

            out = bridge.predict_quality(args.input, model) if model is not None else bridge.predict_quality(args.input)
            print(out)

        else:  # gear
            model = None
            try:
                if args.load_arg:
                    model = bridge.load_gear_model(args.load_arg)
                else:
                    model = bridge.load_gear_model()
            except Exception as e:
                logger.info("Gear model loader not usable (%s). Proceeding without explicit model.", e)

            out = bridge.predict_gear(args.input, model) if model is not None else bridge.predict_gear(args.input)
            print(out)

    except Exception as exc:
        logger.error("Error running prediction: %s", exc)
        sys.exit(2)