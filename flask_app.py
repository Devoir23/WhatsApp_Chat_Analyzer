from flask import Flask, render_template, request
import data_preprocessing
import helper
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

app = Flask(__name__, template_folder="template", static_folder="static")

@app.route('/')
def main():
    return render_template('index.html')

@app.route("/result.html", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file:
            data = uploaded_file.read().decode("utf-8")
            df = data_preprocessing.preprocess(data)

            # Perform data analysis and generate plots
            num_messages, words, num_media_messages, num_links = helper.fetch_stats('Overall', df)
            timeline = helper.monthly_timeline('Overall', df)
            daily_timeline = helper.daily_timeline('Overall', df)
            busy_day = helper.week_activity_map('Overall', df)
            busy_month = helper.month_activity_map('Overall', df)
            user_heatmap = helper.activity_heatmap('Overall', df)
            x, new_df = helper.most_busy_users(df)
            df_wc = helper.create_wordcloud('Overall', df)
            most_common_df = helper.most_common_words('Overall', df)
            # emoji_df = helper.emoji_helper('Overall', df)

            # Convert Matplotlib plots to base64 for embedding in HTML
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            plt.title("Monthly Timeline")
            monthly_timeline_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            plt.title("Daily Timeline")
            daily_timeline_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            plt.title("Most Busy Day")
            busy_day_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            plt.title("Most Busy Month")
            busy_month_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            plt.title("Weekly Activity Map")
            user_heatmap_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax.bar(x.index, x.values, color='red')
            plt.xticks(rotation='vertical')
            plt.title("Most Busy Users")
            most_busy_users_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            plt.title("Wordcloud")
            wordcloud_plot = plot_to_base64(fig)

            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')
            plt.title("Most Common Words")
            most_common_words_plot = plot_to_base64(fig)



            return render_template("result.html", num_messages=num_messages, words=words,
                                   num_media_messages=num_media_messages, num_links=num_links,
                                   monthly_timeline_plot=monthly_timeline_plot,
                                   daily_timeline_plot=daily_timeline_plot, busy_day_plot=busy_day_plot,
                                   busy_month_plot=busy_month_plot, user_heatmap_plot=user_heatmap_plot,
                                   most_busy_users_plot=most_busy_users_plot, wordcloud_plot=wordcloud_plot,
                                   most_common_words_plot=most_common_words_plot,
                                   )

    return render_template("index.html")

def plot_to_base64(fig):
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

if __name__ == "__main__":
    app.run(debug=True)
