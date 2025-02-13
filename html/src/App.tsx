import React, { useState, useEffect } from "react";
import { marked } from "marked";

const App: React.FC = () => {
  const [latestArticle, setLatestArticle] = useState<string>("");
  const [oldArticles, setOldArticles] = useState<string>("");

  const fetchLatestArticle = async () => {
    try {
      let response;
      try {
        response = await fetch("http://localhost:5000/latest_article");
        if (!response.ok) throw new Error("Failed to fetch from port 5000");
      } catch (e) {
        response = await fetch("http://localhost:8000/latest_article");
      }
      const data = await response.json();
      if (data.article) {
        setLatestArticle(data.article);
      }
    } catch (err) {
      console.error("Error fetching latest article:", err);
    }
  };

  const fetchOldArticles = () => {
    fetch("content/ancients.md")
      .then(response => response.text())
      .then(text => setOldArticles(text))
      .catch(err => console.error("Error fetching old articles:", err));
  };

  useEffect(() => {
    fetchLatestArticle();
    fetchOldArticles();
    const interval = setInterval(fetchLatestArticle, 900000); // 15 minutes
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex justify-center p-4">
      <div className="max-w-4xl w-full bg-gray-800 rounded-lg shadow-lg p-6">
        {/* Top Banner */}
        <div className="mb-8 flex justify-center">
          <iframe
            src="http://localhost/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=9&__feature.dashboardSceneSolo"
            width="450"
            height="200"
            frameBorder="0"
            className="rounded-lg shadow-lg"
          ></iframe>
        </div>
        {/* Main Content Row */}
        <div className="md:flex md:space-x-8">
          {/* Latest Article */}
          <section className="md:flex-1 mb-8 md:mb-0">
            <h1 className="text-3xl font-bold mb-4 text-center md:text-left text-blue-400">
              Latest Article
            </h1>
            <div
              className="prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: marked.parse(latestArticle) }}
            />
          </section>
          {/* Right Column: Visualizations */}
          <aside className="md:w-1/2 space-y-4">
            <iframe
              src="http://localhost/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=2&__feature.dashboardSceneSolo"
              width="450"
              height="200"
              frameBorder="0"
              className="rounded-lg shadow-lg"
            ></iframe>
            <iframe
              src="http://localhost/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=1&__feature.dashboardSceneSolo"
              width="450"
              height="200"
              frameBorder="0"
              className="rounded-lg shadow-lg"
            ></iframe>
          </aside>
        </div>
        {/* Old Articles Section */}
        <section className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-center text-blue-400">Old Articles</h2>
          <div className="prose prose-invert max-w-none">
            <details>
              <summary className="cursor-pointer text-xl font-bold mb-2 text-blue-400">
                Show Old Articles
              </summary>
              <div dangerouslySetInnerHTML={{ __html: marked.parse(oldArticles) }} />
            </details>
          </div>
        </section>
      </div>
    </div>
  );
};

export default App;
