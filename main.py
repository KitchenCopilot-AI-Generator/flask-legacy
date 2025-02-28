"""
Fridge Recipe Generator - Main entry point for the application

This application:
1. Analyzes fridge/food images to identify ingredients
2. Generates recipe suggestions based on available ingredients

The application can be run in:
- CLI mode for direct command line use
- API mode for integration with other applications or frontends
"""

import argparse
import os
import uvicorn
from typing import Optional

# Import services and config
from config import Config
from services.azure_client import AzureClientService
from services.vision_service import VisionService
from services.recipe_service import RecipeService
from api.routes import app as api_app

class CLIProcessor:
    """Command-line interface processor for the application"""
    
    def __init__(self, config, vision_service, recipe_service):
        """
        Initialize CLI processor
        
        Args:
            config: Configuration object
            vision_service: Vision analysis service
            recipe_service: Recipe generation service
        """
        self.config = config
        self.vision_service = vision_service
        self.recipe_service = recipe_service
    
    def analyze_image(self, image_filename: str) -> dict:
        """
        Analyze a fridge/food image and identify ingredients
        
        Args:
            image_filename: Filename of the image to analyze
            
        Returns:
            Analysis result
        """
        paths = self.config.get_file_paths(image_filename)
        print(f"Analyzing image: {paths['input_image']}")
        
        # Run analysis
        result = self.vision_service.analyze_image(paths["input_image"])
        
        # Save result
        output_path = self.vision_service.save_analysis(result, paths["vision_output"])
        print(f"Analysis saved to {output_path}")
        
        # Get summary
        summary = self.vision_service.get_ingredients_summary(result)
        print(f"\nFound {summary['total_count']} ingredients in {summary['categories']} categories:")
        for category, count in summary["by_category"].items():
            print(f"- {category}: {count} items")
        
        return result
    
    def generate_recipes(self, image_filename: Optional[str] = None, num_recipes: int = 5) -> dict:
        """
        Generate recipe suggestions based on available ingredients
        
        Args:
            image_filename: Optional filename of previously analyzed image
            num_recipes: Number of recipes to generate
            
        Returns:
            Generated recipes
        """
        paths = self.config.get_file_paths(image_filename)
        
        # Check if ingredients file exists
        if not os.path.exists(paths["vision_output"]):
            print("No ingredients analysis found. Please analyze an image first.")
            return {}
        
        # Load ingredients
        ingredients = self.recipe_service.load_ingredients(paths["vision_output"])
        print(f"Loaded {len(ingredients)} ingredients from analysis")
        
        # Generate recipes
        print(f"Generating {num_recipes} recipe suggestions...")
        recipes_data = self.recipe_service.generate_recipes(ingredients, num_recipes=num_recipes)
        
        # Save recipes
        output_path = self.recipe_service.save_recipes(recipes_data, paths["recipes_output"])
        print(f"Recipes saved to {output_path}")
        
        # Print recipe analysis
        df = self.recipe_service.get_recipes_analysis(recipes_data)
        if df is not None:
            print("\n==== RECIPE ANALYSIS ====")
            print(df)
        else:
            print("No recipes were generated.")
        
        return recipes_data

def setup_api_mode():
    """
    Set up the application in API mode
    
    Returns:
        FastAPI application instance
    """
    # Initialize configuration
    app_config = Config()
    
    # Initialize services
    azure_client = AzureClientService(app_config)
    app_vision_service = VisionService(azure_client)
    app_recipe_service = RecipeService(azure_client)
    
    # Set up API services
    import api.routes as routes
    routes.config = app_config
    routes.vision_service = app_vision_service
    routes.recipe_service = app_recipe_service
    
    return api_app

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Fridge Recipe Generator")
    parser.add_argument("--mode", choices=["cli", "api"], default="api", help="Run mode (cli or api)")
    parser.add_argument("--action", choices=["analyze", "recipes", "both"], default="both", help="Action to perform in CLI mode")
    parser.add_argument("--image", help="Image filename for analysis (in input directory)")
    parser.add_argument("--recipes", type=int, default=5, help="Number of recipes to generate")
    parser.add_argument("--host", default="127.0.0.1", help="Host for API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        # API mode
        api_app = setup_api_mode()
        print(f"Starting API server on {args.host}:{args.port}")
        uvicorn.run(api_app, host=args.host, port=args.port)
    else:
        # CLI mode
        config = Config()
        azure_client = AzureClientService(config)
        vision_service = VisionService(azure_client)
        recipe_service = RecipeService(azure_client)
        
        cli = CLIProcessor(config, vision_service, recipe_service)
        
        if args.action in ["analyze", "both"]:
            if not args.image:
                print("Error: Image filename required for analysis")
                return
            cli.analyze_image(args.image)
        
        if args.action in ["recipes", "both"]:
            cli.generate_recipes(args.image, args.recipes)

if __name__ == "__main__":
    main()