import tempfile
import unittest
from pathlib import Path

from .helpers import import_generator_module

generator = import_generator_module("generator")
make_slug = generator.make_slug
resolve_dashboard_config = generator.resolve_dashboard_config
write_dashboard = generator.write_dashboard


class GeneratorTest(unittest.TestCase):
    def test_slug_generation(self):
        self.assertEqual(make_slug("Sala e Cozinha"), "sala-e-cozinha")
        self.assertEqual(make_slug("  Geração Árvore  "), "geracao-arvore")
        self.assertEqual(make_slug(""), "dashboard")

    def test_hybrid_area_and_explicit_entities(self):
        config = {
            "name": "BD Mobile",
            "rooms": [
                {
                    "name": "Sala",
                    "area": "sala",
                    "entities": {
                        "light": [
                            {
                                "entity_id": "light.manual_lamp",
                                "name": "Manual Lamp",
                            }
                        ]
                    },
                    "exclude": ["light.excluded"],
                    "overrides": {
                        "light.area_lamp": {"name": "Area Lamp Override"},
                    },
                }
            ],
        }
        registry = [
            {"entity_id": "light.area_lamp", "area_id": "sala", "name": "Area Lamp"},
            {"entity_id": "light.excluded", "area_id": "sala", "name": "Excluded"},
            {"entity_id": "cover.window", "area_id": "sala", "name": "Window"},
            {"entity_id": "automation.skip_me", "area_id": "sala", "name": "Skip"},
        ]

        resolved = resolve_dashboard_config(config, registry)
        room = resolved["rooms"][0]
        lights = room["entities_by_domain"]["light"]
        self.assertEqual([entity["entity_id"] for entity in lights], ["light.area_lamp", "light.manual_lamp"])
        self.assertEqual(lights[0]["name"], "Area Lamp Override")
        self.assertEqual(room["entities_by_domain"]["cover"][0]["entity_id"], "cover.window")

    def test_write_dashboard_files_without_helper_entities(self):
        config = {
            "name": "Generated Test",
            "overview": {"weather_entity": "sensor.weather_entity_forecast"},
            "rooms": [
                {
                    "name": "Office",
                    "entities": {
                        "light": ["light.office_main", "light.office_desk"],
                        "sensor": [{"entity_id": "sensor.remote_battery", "device_class": "battery"}],
                    },
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            generated = write_dashboard(config, temp_dir)
            dashboard = Path(temp_dir) / generated.slug / "dashboard.yaml"
            room_view = Path(temp_dir) / generated.slug / "views/rooms/00-office.yaml"

            self.assertTrue(dashboard.exists())
            self.assertTrue(room_view.exists())
            source = "\n".join(path.read_text() for path in Path(temp_dir, generated.slug).rglob("*.yaml"))
            self.assertNotIn("platform: group", source)
            self.assertIn("light.office_main", source)
            self.assertIn("hc_battery_card", source)

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            resolve_dashboard_config({"rooms": []})


if __name__ == "__main__":
    unittest.main()
