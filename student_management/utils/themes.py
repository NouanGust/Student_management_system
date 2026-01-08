import flet as ft

class ThemeManager:
    @staticmethod
    def get_theme(theme_name: str):
        """Retorna a configuração do tema escolhido"""
        
        # 1. STUDIO DARK (Foco e Contraste)
        if theme_name == "dark":
            return {
                "mode": ft.ThemeMode.DARK,
                "seed": ft.colors.DEEP_PURPLE,
                "bgcolor": "#1A1C1E"
            }
            
        # 2. TECH CLEAN (Minimalista e Corporativo)
        elif theme_name == "light":
            return {
                "mode": ft.ThemeMode.LIGHT,
                "seed": ft.colors.INDIGO,
                "bgcolor": "#F8F9FA"
            }
            
        # 3. CREATIVE ENERGY (Laranja/Coral vibrante)
        elif theme_name == "creative":
            return {
                "mode": ft.ThemeMode.LIGHT, # ou DARK se preferir
                "seed": ft.colors.ORANGE,
                "bgcolor": "#FFF3E0"
            }
            
        # Padrão (Tech Clean)
        return {
            "mode": ft.ThemeMode.LIGHT,
            "seed": ft.colors.BLUE,
            "bgcolor": ft.colors.WHITE
        }

    @staticmethod
    def apply_theme(page: ft.Page, theme_name: str):
        """Aplica o tema na página"""
        config = ThemeManager.get_theme(theme_name)
        
        page.theme_mode = config["mode"]
        page.theme = ft.Theme(
            color_scheme_seed=config["seed"],
            use_material3=True,
            visual_density=ft.VisualDensity.COMFORTABLE
        )
        
        # Se quiser forçar cor de fundo específica além do tema
        # page.bgcolor = config["bgcolor"] 
        
        page.update()