from abc import ABC, abstractmethod

import os
from typing import Type, Dict


class AbstractObserver(ABC):
    @staticmethod
    def load_templates_from_folder(folder: str, class_from_template_image: Type) -> Dict:
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Templates directory not found: {folder}")

        dict_to_return = {}
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            base_name = os.path.splitext(file_name)[0]

            if os.path.isfile(file_path):
                dict_to_return[base_name] = class_from_template_image(file_path)
        return dict_to_return
