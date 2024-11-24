import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Scrollbar, Text
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import openai 

BACKGROUND_COLOR = '#f7f7f7'
PRIMARY_COLOR = '#007BFF'
SECONDARY_COLOR = '#FF5733'
TEXT_COLOR = 'black'

# Judge will provide us with a functional one 
openai.api_key = "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"
data_columns = ['air_quality_index', 'noise_level', 'green_space_area', 'land_surface_temp',
                'temperature', 'humidity', 'precipitation', 'population_density', 
                'crime_rate', 'mental_health_score']

# Creating a window for ChatGPT
root = tk.Tk()
root.title("ChatGPT Assistant")

def load_data(file_path):
    return pd.read_csv(file_path)

def validate_data(data):
    required_columns = ['air_quality_index', 'noise_level', 'green_space_area',
                        'land_surface_temp', 'temperature', 'humidity', 
                        'precipitation', 'population_density', 'crime_rate', 
                        'mental_health_score']
    missing_columns = [col for col in required_columns if col not in data.columns]
    return missing_columns

def train_model(data):
    features = ['air_quality_index', 'noise_level', 'green_space_area',
                'land_surface_temp', 'temperature', 'humidity', 
                'precipitation', 'population_density', 'crime_rate']
    
    X = data[features]
    y = data['mental_health_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)

    return y_test, predictions, model, features, mse, r2, mae

def visualize_results(y_test, predictions, model, features, data, metrics):
    interactive_figs = {}
    
    scatter_fig = px.scatter(x=y_test, y=predictions, labels={'x': 'Actual Mental Health Score', 'y': 'Predicted Mental Health Score'},
                             title='Actual vs Predicted Mental Health Scores',
                             color_discrete_sequence=['#007BFF'])
    
    z = np.polyfit(y_test, predictions, 1)
    p = np.poly1d(z)
    scatter_fig.add_traces(go.Scatter(x=y_test, y=p(y_test), mode='lines', name='Line of Best Fit',
                                        line=dict(dash='dash', color='#FF5733')))
    scatter_fig.add_traces(go.Scatter(x=y_test, y=y_test, mode='lines', name='Perfect Prediction',
                                        line=dict(dash='dash', color='#28A745')))
    
    scatter_fig.update_traces(marker=dict(size=8),
                              hovertemplate="Actual: %{x}<br>Predicted: %{y}")
    interactive_figs['scatter'] = scatter_fig

    errors = y_test - predictions
    error_fig = px.histogram(errors, x=errors, nbins=30, title='Error Distribution', 
                              labels={'x': 'Error (Actual - Predicted)', 'y': 'Frequency'},
                              color_discrete_sequence=['#007BFF'])
    error_fig.add_vline(0, line_color='red', line_dash='dash', annotation_text='Zero Error Line', annotation_position='top right')
    interactive_figs['error'] = error_fig

    feature_importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    importance_fig = px.bar(feature_importances, x=feature_importances.index, y=feature_importances.values, 
                             title='Feature Importance', labels={'x': 'Features', 'y': 'Importance Score'},
                             color_discrete_sequence=['#FF5733'])
    
    interactive_figs['importance'] = importance_fig

    summary_fig = go.Figure()
    summary_fig.add_trace(go.Bar(x=['Mean Squared Error', 'R-squared', 'Mean Absolute Error'],
                                  y=metrics,
                                  marker_color=['#9467bd', '#8c564b', '#e377c2']))
    summary_fig.update_layout(title='Summary of Key Metrics', xaxis_title='Metrics', yaxis_title='Values',
                              yaxis=dict(range=[0, max(metrics) + 1]))

    correlation_matrix = data[features + ['mental_health_score']].corr()
    corr_fig = px.imshow(correlation_matrix, title='Correlation Heatmap', color_continuous_scale='Viridis',
                         labels=dict(x='Features', y='Features', color='Correlation Coefficient'))
    
    for i in range(correlation_matrix.shape[0]):
        for j in range(correlation_matrix.shape[1]):
            corr_fig.add_annotation(text=f"{correlation_matrix.iloc[i, j]:.2f}",
                                    x=j, y=i, showarrow=False, font=dict(size=10, color='black'))
    
    interactive_figs['correlation'] = corr_fig

    return interactive_figs, summary_fig

# ChatGPT Assistant Interaction Panel
def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful mental health assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# ChatGPT Interaction Interface
def add_chat_interface():
    chat_frame = tk.Frame(root, bg=BACKGROUND_COLOR, relief='groove', borderwidth=2)
    chat_frame.pack(side='right', fill='both', padx=10, pady=10, expand=True)

    chat_label = tk.Label(chat_frame, text="Chat with Assistant", font=("Arial", 14), bg=BACKGROUND_COLOR, fg=PRIMARY_COLOR)
    chat_label.pack(pady=5)

    chat_display = Text(chat_frame, wrap='word', font=("Arial", 12), bg='white', state='disabled', height=20)
    chat_display.pack(expand=True, fill='both', padx=5, pady=5)

    scrollbar = Scrollbar(chat_frame, command=chat_display.yview)
    scrollbar.pack(side='right', fill='y')
    chat_display.config(yscrollcommand=scrollbar.set)

    input_frame = tk.Frame(chat_frame, bg=BACKGROUND_COLOR)
    input_frame.pack(fill='x', padx=5, pady=5)

    input_box = tk.Entry(input_frame, font=("Arial", 12))
    input_box.pack(side='left', fill='x', expand=True, padx=(0, 5))

# To store the message input by the User and the response generated by ChatGPT
    def send_message():
        user_message = input_box.get()
        if user_message.strip():
            chat_display.config(state='normal')
            chat_display.insert('end', f"User: {user_message}\n")
            chat_display.config(state='disabled')

            response = chat_with_gpt(user_message)

            chat_display.config(state='normal')
            chat_display.insert('end', f"Assistant: {response}\n\n")
            chat_display.see('end')
            chat_display.config(state='disabled')

            input_box.delete(0, 'end')

    send_button = tk.Button(input_frame, text="Send", command=send_message, bg=PRIMARY_COLOR, fg='white', font=("Arial", 12), borderwidth=0)
    send_button.pack(side='right')

    style_button(send_button)

# Code breaks if utilized without API key with credits
'''
def chatgpt_insight(data, mental_health_score):
    """
    Modify the ChatGPT prompt to include the mental health score and other key features.
    This will ensure that the analysis incorporates the mental health score and its impact.
    
    :param data: The data being analyzed
    :param mental_health_score: The current mental health score from the dataset
    :return: A response from ChatGPT with the insights
    """
    
    data_summary = f"The dataset includes the following features: {', '.join(data_columns)}. "
    
    sample_data = f"Example row: air_quality_index= {data['air_quality_index'][0]}, noise_level= {data['noise_level'][0]}, green_space_area= {data['green_space_area'][0]}, etc."
    
    mental_health_context = f"The current mental health score is {mental_health_score}."

    prompt = f"""
    Please analyze the following dataset with a focus on mental health score. 
    The dataset includes features such as air quality, noise levels, green space, temperature, etc.
    Use this information to provide insights and make recommendations based on the mental health score of {mental_health_score}. 
    
    {data_summary}
    {sample_data}
    {mental_health_context}
    """

    response = openai.Completion.create(
        model="gpt-4",  
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].text.strip()

file_path = "C:/Users/GamaZone/Desktop/Coding/IBDP Hackathon 24/urban_mental_health_data.csv  "
data = load_data(file_path)

mental_health_score = data['mental_health_score'][0]

insights = chatgpt_insight(data, mental_health_score)

print("ChatGPT Insights on Data and Mental Health Score:\n", insights)
'''

def qualitative_analysis(data):
    bullet_points = []
    
    if 'noise_level' in data.columns:
        noise_mean = data['noise_level'].mean()
        bullet_points.append(f"- Average Noise Level: {noise_mean:.2f} dB")
    
    if 'air_quality_index' in data.columns:
        air_quality_mean = data['air_quality_index'].mean()
        bullet_points.append(f"- Average Air Quality Index: {air_quality_mean:.2f}")

    total_records = data.shape[0]
    bullet_points.append(f"- Total Records: {total_records}")

    mental_health_mean = data['mental_health_score'].mean()
    bullet_points.append(f"- Average Mental Health Score: {mental_health_mean:.2f}")
    bullet_points.append(f"- Mental Health Score Range: {data['mental_health_score'].min()} to {data['mental_health_score'].max()}")

    if total_records > 0:
        bullet_points.append(f"- Average Temperature: {data['temperature'].mean():.2f}°C")
        bullet_points.append(f"- Average Humidity: {data['humidity'].mean():.2f}%")

        if mental_health_mean < 50:
            bullet_points.append("  * Warning: Average Mental Health Score is below 50, indicating potential mental health concerns in the population.")
        else:
            bullet_points.append("  * Note: Average Mental Health Score is above 50, indicating relatively better mental health status.")

        if air_quality_mean > 100:
            bullet_points.append("  * Alert: Average Air Quality Index is above 100, which may be unhealthy for sensitive groups.")
        else:
            bullet_points.append("  * Note: Average Air Quality Index is within safe limits.")

    return bullet_points

def get_chatgpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo", 
            prompt=prompt,
            max_tokens=150,  
            n=1,
            stop=None,
            temperature=0.7
        )
        message = response.choices[0].text.strip()
        return message
    except Exception as e:
        print(f"Error with ChatGPT API: {e}")
        return "Sorry, there was an error processing your request."

def ask_chatgpt():
    user_question = chatgpt_entry.get() 
    prompt = f"User asked: {user_question}\nProvide a helpful and informative response."
    
    response = get_chatgpt_response(prompt)
    chatgpt_response_label.config(text=response)  

chatgpt_entry = tk.Entry(root, font=("Arial", 12), width=40)
chatgpt_entry.pack(pady=10)

ask_button = tk.Button(root, text="Ask ChatGPT", command=ask_chatgpt, bg=PRIMARY_COLOR, fg='white', font=("Arial", 12), borderwidth=0)
ask_button.pack(pady=10)

chatgpt_response_label = tk.Label(root, text="ChatGPT response will appear here.", font=("Arial", 12), bg=BACKGROUND_COLOR)
chatgpt_response_label.pack(pady=10)

def on_closing():
    root.quit()

def show_interactive_plot(fig):
    fig.show()

def show_help():
    help_message = (
        "Help Section:\n\n"
        "1. Upload Dataset: Use the 'Upload Dataset' button to select a CSV file with the required columns:\n"
        "   - air_quality_index\n"
        "   - noise_level\n"
        "   - green_space_area\n"
        "   - land_surface_temp\n"
        "   - temperature\n"
        "   - humidity\n"
        "   - precipitation\n"
        "   - population_density\n"
        "   - crime_rate\n"
        "   - mental_health_score\n"
        "2. View Visualizations: After uploading, view visualizations like:\n"
        "   - Actual vs Predicted Scores\n"
        "   - Error Distribution\n"
        "   - Feature Importance\n"
        "   - Correlation Heatmap\n"
        "3. Quit: Use the close button to exit the application."
    )
    messagebox.showinfo("Help", help_message)

def on_closing():
    root.quit()

def show_interactive_plot(fig):
    fig.show()

def show_requirements():
    requirements_window = Toplevel(root)
    requirements_window.title("Required Columns")
    requirements_window.geometry("700x500")
    
    requirements_text = Text(requirements_window, wrap='word', font=("Arial", 12))
    requirements_text.pack(expand=True, fill='both')

    scrollbar = Scrollbar(requirements_window, command=requirements_text.yview)
    scrollbar.pack(side='right', fill='y')
    requirements_text.config(yscrollcommand=scrollbar.set)

    requirements = (
        "Required Columns for the CSV File:\n\n"
        "╔══════════════════════════════════════════════════════════════════════════════╗\n"
        "║ Column Name              ║ Description                                         ║\n"
        "╠══════════════════════════════════════════════════════════════════════════════╣\n"
        "║ air_quality_index        ║ Float: Air Quality Index (AQI).                    ║\n"
        "║ noise_level              ║ Float: Noise level in decibels.                    ║\n"
        "║ green_space_area         ║ Float: Area of green space in square meters.       ║\n"
        "║ land_surface_temp        ║ Float: Land surface temperature in degrees Celsius. ║\n"
        "║ temperature              ║ Float: Ambient temperature in degrees Celsius.     ║\n"
        "║ humidity                 ║ Float: Relative humidity in percentage.            ║\n"
        "║ precipitation            ║ Float: Total precipitation in millimeters.        ║\n"
        "║ population_density       ║ Float: Population density per square kilometer.    ║\n"
        "║ crime_rate               ║ Float: Crime rate per 1000 people.                ║\n"
        "║ mental_health_score      ║ Integer: Mental health score (0-100).              ║\n"
        "╚══════════════════════════════════════════════════════════════════════════════╝\n"
    )

    requirements_text.insert('end', requirements)
    requirements_text.config(state='disabled')

    footer_text = "\n\nFor ease of testing, we've compiled sample data. You can also input your own data as per the column names specified above."
    requirements_text.config(state='normal')
    requirements_text.insert('end', footer_text)
    requirements_text.config(state='disabled')

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        data = load_data(file_path)
        missing_columns = validate_data(data)
        
        if missing_columns:
            messagebox.showerror("Error", f"The following columns are missing: {', '.join(missing_columns)}")
            return
        
        y_test, predictions, model, features, mse, r2, mae = train_model(data)
        metrics = [mse, r2, mae]
        interactive_figs, summary_fig = visualize_results(y_test, predictions, model, features, data, metrics)

        qualitative_points = qualitative_analysis(data)

        for widget in root.winfo_children():
            widget.destroy()

        heading_label = tk.Label(root, text="Mental Health Prediction Dashboard", font=("Arial", 16), bg=BACKGROUND_COLOR)
        heading_label.pack(pady=10)

        summary_graphical_button = tk.Button(root, text="Show Summary (Graphical)", command=lambda: show_interactive_plot(summary_fig), bg=SECONDARY_COLOR, fg='white', font=("Arial", 12), borderwidth=0)
        summary_graphical_button.pack(pady=5)
        style_button(summary_graphical_button)

        summary_descriptive_button = tk.Button(root, text="Show Summary (Descriptive)", command=lambda: show_summary(qualitative_points), bg='#28A745', fg='white', font=("Arial", 12), borderwidth=0)
        summary_descriptive_button.pack(pady=5)
        style_button(summary_descriptive_button)

        for i, (title, fig) in enumerate(interactive_figs.items()):
            button = tk.Button(root, text=f"Show {title.capitalize()} Plot", command=lambda f=fig: show_interactive_plot(f), bg=PRIMARY_COLOR, fg='white', font=("Arial", 12), borderwidth=0)
            button.pack(pady=5)
            style_button(button)

        help_button = tk.Button(root, text="Help", command=show_help, bg=PRIMARY_COLOR, fg='white', font=("Arial", 12), borderwidth=0)
        help_button.pack(pady=5)
        style_button(help_button)

        transparency_button = tk.Button(root, text="Show Algorithmic Transparency", command=show_transparency, bg='#FF4500', fg='white', font=("Arial", 12), borderwidth=0)
        transparency_button.pack(pady=5)
        style_button(transparency_button)

        operations_label = tk.Label(root, text="Mathematical Operations and Decision-Making Process:", font=("Arial", 14), bg=BACKGROUND_COLOR)
        operations_label.pack(pady=10)

        operations_text = Text(root, wrap='word', font=("Arial", 12))
        operations_text.pack(expand=True, fill='both')

        operations_info = (
            "1. Data Splitting:\n"
            f"   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n"
            f"   Here, 'X' consists of the features: {', '.join(features)}\n"
            f"   And 'y' is the target variable: 'mental_health_score'.\n\n"
            "2. Model Training:\n"
            "   model = RandomForestRegressor(n_estimators=100, random_state=42)\n"
            "   model.fit(X_train, y_train)\n\n"
            "3. Predictions:\n"
            "   predictions = model.predict(X_test)\n\n"
            "4. Evaluation Metrics:\n"
            "   - Mean Squared Error (MSE): MSE = (1/n) * Σ(actual - predicted)²\n"
            "   - R-squared: R² = 1 - (Σ(actual - predicted)² / Σ(actual - mean(actual))²)\n"
            "   - Mean Absolute Error (MAE): MAE = (1/n) * Σ|actual - predicted|\n"
        )

        operations_text.insert('end', operations_info)
        operations_text.config(state='disabled')

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)

def show_summary(bullet_points):
    summary_window = Toplevel(root)
    summary_window.title("Descriptive Summary")
    summary_window.geometry("600x400")

    summary_text = Text(summary_window, wrap='word', font=("Arial", 12))
    summary_text.pack(expand=True, fill='both')

    for point in bullet_points:
        summary_text.insert('end', point + "\n")
    
    summary_text.config(state='disabled')

def style_button(button):
    button.config(relief="flat", bd=0, highlightthickness=0)
    button.bind("<Enter>", lambda e: button.config(bg='#0056b3'))
    button.bind("<Leave>", lambda e: button.config(bg=button.cget("bg")))

def show_transparency():
    transparency_window = Toplevel(root)
    transparency_window.title("Algorithmic Transparency")
    transparency_window.geometry("700x500")
    
    transparency_text = Text(transparency_window, wrap='word', font=("Arial", 12))
    transparency_text.pack(expand=True, fill='both')

    transparency_info = (
        "Algorithmic Transparency Overview:\n\n"
        "This application employs a Random Forest Regressor to predict mental health scores based on various environmental and social factors.\n"
        "The model is trained using the following steps:\n"
        "1. Data Loading: Data is loaded from the provided CSV file.\n"
        "2. Data Validation: The application checks for missing columns and informs the user if any are absent.\n"
        "3. Feature Selection: The model uses several features such as air quality index, noise level, etc.\n"
        "4. Model Training: The model is trained using the training dataset, where it learns the relationship between the features and the mental health score.\n"
        "5. Predictions: After training, the model makes predictions on the test dataset.\n"
        "6. Evaluation: The model's performance is evaluated using metrics like Mean Squared Error (MSE), R-squared (R²), and Mean Absolute Error (MAE).\n\n"
        "Ethical Considerations:\n"
        "- The model aims to provide insights into mental health factors but is not a substitute for professional evaluation.\n"
        "- Care should be taken in interpreting the predictions, as they can vary based on the quality of the input data.\n\n"
        "Limitations:\n"
        "- The model's accuracy depends on the completeness and quality of the data provided.\n"
        "- Potential biases in the data may affect the predictions."
    )

    transparency_text.insert('end', transparency_info)
    transparency_text.config(state='disabled')

root = tk.Tk()
root.title("Mental Health Prediction Visualization")
root.geometry("400x600")
root.configure(bg=BACKGROUND_COLOR)

heading_label = tk.Label(root, text="Mental Health Prediction Dashboard", font=("Arial", 16), bg=BACKGROUND_COLOR)
heading_label.pack(pady=10)

requirements_button = tk.Button(root, text="Show Requirements", command=show_requirements, bg='#FFD700', fg=TEXT_COLOR, font=("Arial", 12), borderwidth=0)
requirements_button.pack(pady=10)
style_button(requirements_button)

upload_button = tk.Button(root, text="Upload Dataset", command=upload_file, bg=PRIMARY_COLOR, fg='white', font=("Arial", 12, "bold"), borderwidth=0)
upload_button.pack(pady=10)
style_button(upload_button)

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    root.mainloop()