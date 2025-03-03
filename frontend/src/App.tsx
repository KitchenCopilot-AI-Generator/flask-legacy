import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import IngredientsList from './components/IngredientsList';
import RecipesList from './components/RecipesList';
import { analyzeImage, generateRecipes } from './api/api';
import './index.css';

// Define types for state variables
interface Ingredient {
  name: string;
}

interface Recipe {
  title: string;
  ingredients: string[];
  instructions: string;
}

const App: React.FC = () => {
  // State for ingredients, recipes, loading states, and errors
  const [ingredients, setIngredients] = useState<Ingredient[] | null>(null);
  const [recipes, setRecipes] = useState<Recipe[] | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isGeneratingRecipes, setIsGeneratingRecipes] = useState<boolean>(false);
  const [ingredientsError, setIngredientsError] = useState<string | null>(null);
  const [recipesError, setRecipesError] = useState<string | null>(null);

  // Handle analyze image
  const handleAnalyzeImage = async (imageFile: File) => {
    try {
      // Reset states
      setIngredients(null);
      setRecipes(null);
      setIngredientsError(null);
      setRecipesError(null);

      console.log("Starting image analysis...");
      // Start loading
      setIsAnalyzing(true);

      // Analyze image
      const analysisResult: Ingredient[] = await analyzeImage(imageFile);
      console.log("Analysis completed with result:", analysisResult);

      // Set ingredients
      setIngredients(analysisResult);
      console.log("Ingredients state set with:", analysisResult);

      console.log("Starting recipe generation...");
      // Generate recipes
      setIsGeneratingRecipes(true);
      const recipesResult: Recipe[] = await generateRecipes(5);
      console.log("Recipes generated with result:", recipesResult);

      // Set recipes
      setRecipes(recipesResult);
      console.log("Recipes state set with:", recipesResult);
    } catch (error) {
      console.error('Error in analyze workflow:', error);

      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';

      if (!ingredients) {
        setIngredientsError(errorMessage);
      } else {
        setRecipesError(errorMessage);
      }
    } finally {
      // Stop loading
      console.log("Setting loading states to false");
      setIsAnalyzing(false);
      setIsGeneratingRecipes(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">AI Recipe Generator</h1>
        <p className="app-subtitle">Upload a photo of your ingredients and get recipe suggestions!</p>
      </header>

      <main className="container">
        <div className="grid grid-cols-2">
          <div className="section">
            {/* Image Upload Section */}
            <ImageUpload 
              onAnalyzeImage={handleAnalyzeImage} 
              isLoading={isAnalyzing || isGeneratingRecipes} 
            />

            {/* Ingredients Section */}
            {(ingredients || isAnalyzing || ingredientsError) && (
              <IngredientsList 
                ingredients={ingredients} 
                isLoading={isAnalyzing} 
                error={ingredientsError}
              />
            )}
          </div>

          <div className="section">
            {/* Recipes Section */}
            {(recipes || isGeneratingRecipes || recipesError) && (
              <RecipesList 
                recipes={recipes} 
                isLoading={isGeneratingRecipes} 
                error={recipesError}
              />
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; {new Date().getFullYear()} Fridge Recipe Generator</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
