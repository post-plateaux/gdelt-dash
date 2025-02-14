import React, { useState, useEffect, useRef } from "react";
import { marked } from "marked";

// Configure marked options
const renderer = new marked.Renderer();
renderer.link = (href, title, text) => {
  return `<a href="${href}" target="_blank" rel="noopener noreferrer" ${
    title ? `title="${title}"` : ""
  }>${text}</a>`;
};
marked.setOptions({
  renderer,
  breaks: true,
  gfm: true,
  headerIds: false,
  pedantic: false,
  sanitize: false,
  smartLists: true,
  smartypants: false,
});

const App: React.FC = () => {
  // Initialize darkMode based on system preference
  const [darkMode, setDarkMode] = useState<boolean>(
    window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  // Apply or remove the dark class on the html element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  // Toggle dark mode state
  const toggleDarkMode = () => setDarkMode(prev => !prev);

  const [latestArticle, setLatestArticle] = useState<string>("");
  const [oldArticles, setOldArticles] = useState<string[]>([]);
  const [modalContent, setModalContent] = useState<string>("");

  const [showOverviewModal, setShowOverviewModal] = useState<boolean>(false);
  const [closingOverview, setClosingOverview] = useState<boolean>(false);

  const [showArticleModal, setShowArticleModal] = useState<boolean>(false);
  const [closingArticle, setClosingArticle] = useState<boolean>(false);
  const [selectedArticle, setSelectedArticle] = useState<string>("");

  const overviewModalRef = useRef<HTMLDivElement>(null);
  const articleModalRef = useRef<HTMLDivElement>(null);

  const [scrollProgress, setScrollProgress] = useState<number>(0);

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
      .then((response) => response.text())
      .then((text) => {
        const articleMatches = text.match(/<details>[\s\S]*?<\/details>/g) || [];
        setOldArticles(articleMatches);
      })
      .catch((err) => console.error("Error fetching old articles:", err));
  };

  const fetchModalContent = () => {
    fetch("content/overview.md")
      .then((response) => response.text())
      .then((text) => setModalContent(text))
      .catch((err) => console.error("Error fetching modal content:", err));
  };

  useEffect(() => {
    fetchLatestArticle();
    fetchOldArticles();
    fetchModalContent();
    const interval = setInterval(fetchLatestArticle, 900000);
    return () => clearInterval(interval);
  }, []);

  // Scroll progress indicator effect
  useEffect(() => {
    const handleScroll = () => {
      const winScroll = window.scrollY;
      const height = document.body.scrollHeight - window.innerHeight;
      const scrolled = (winScroll / height) * 100;
      setScrollProgress(scrolled);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const overviewContent = latestArticle;

  const extractArticleTitle = (articleContent: string) => {
    const titleMatch = articleContent.match(/<summary>(.*?)<\/summary>/);
    return titleMatch ? titleMatch[1] : "Untitled Article";
  };

  const extractArticleBody = (articleContent: string) => {
    const bodyMatch = articleContent.match(/<\/summary>([\s\S]*?)$/);
    return bodyMatch ? bodyMatch[1].trim() : "";
  };

  const processArticleContent = (articleContent: string) => {
    return articleContent
      .replace(/<details>/, "")
      .replace(/<\/details>/, "")
      .replace(/<summary>.*?<\/summary>/, "")
      .trim();
  };

  const handleCloseOverviewModal = () => {
    setClosingOverview(true);
    setTimeout(() => {
      setShowOverviewModal(false);
      setClosingOverview(false);
    }, 200);
  };

  const handleCloseArticleModal = () => {
    setClosingArticle(true);
    setTimeout(() => {
      setShowArticleModal(false);
      setClosingArticle(false);
      setSelectedArticle("");
    }, 200);
  };

  const handleBackToTopOverview = () => {
    overviewModalRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleBackToTopArticle = () => {
    articleModalRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex justify-center p-4 dark:bg-gray-900 dark:text-gray-100">
      {/* Scroll Progress Indicator */}
      <div className="fixed top-0 left-0 z-50">
        <div className="h-1 bg-blue-500" style={{ width: `${scrollProgress}%` }} />
      </div>
      <div className="max-w-4xl w-full bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-lg p-6 relative">
        {/* Dark mode toggle */}
        <div className="absolute top-4 left-4">
          <button
            className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
            onClick={toggleDarkMode}
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
        {/* About this Project button */}
        <div className="absolute top-4 right-4">
          <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
            onClick={() => setShowOverviewModal(true)}
          >
            About this Project
          </button>
        </div>
        {/* Top Banner */}
        <div className="mb-8 flex justify-center">
          <iframe
            src="http://localhost/gdelt/d-solo/ee25sajexuupsc/gdelt?orgId=1&amp;timezone=browser&amp;panelId=9&amp;__feature.dashboardSceneSolo"
            frameBorder="0"
            className="w-full h-[200px] md:h-[250px] lg:h-[300px] rounded-lg shadow-lg"
          ></iframe>
        </div>
        {/* Overview Section */}
        <section className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-center text-blue-700 dark:text-blue-400">
            Overview of the Last 15
          </h2>
          <div
            className="prose dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: marked.parse(overviewContent) }}
          />
        </section>
        {/* Divider with a visual element */}
        <div className="my-8 flex items-center">
          <hr className="flex-grow border-t border-gray-700" />
          <div className="mx-4">
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
          </div>
          <hr className="flex-grow border-t border-gray-700" />
        </div>
        {/* Visualizations Section */}
        <section className="mt-4">
          <div className="flex flex-col md:flex-row md:space-x-8">
            <iframe
              src="http://localhost/gdelt/d-solo/ee25sajexuupsc/gdelt?orgId=1&amp;timezone=browser&amp;panelId=2&amp;__feature.dashboardSceneSolo"
              frameBorder="0"
              className="w-full h-[200px] md:h-[250px] lg:h-[300px] rounded-lg shadow-lg mb-4 md:mb-0"
            ></iframe>
            <iframe
              src="http://localhost/gdelt/d-solo/ee25sajexuupsc/gdelt?orgId=1&amp;timezone=browser&amp;panelId=1&amp;__feature.dashboardSceneSolo"
              frameBorder="0"
              className="w-full h-[200px] md:h-[250px] lg:h-[300px] rounded-lg shadow-lg"
            ></iframe>
          </div>
        </section>
        {/* Old Articles Section */}
        <section className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-center text-blue-400">
            Old Articles
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {oldArticles.map((article, index) => (
              <div
                key={index}
                className="bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-300 rounded-lg p-4 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transform hover:scale-105 transition-all duration-300"
                onClick={() => {
                  setSelectedArticle(article);
                  setShowArticleModal(true);
                }}
              >
                <h3 className="text-lg font-bold text-blue-700 dark:text-blue-300">
                  {extractArticleTitle(article)}
                </h3>
                <p className="text-sm text-gray-800 dark:text-gray-300 line-clamp-3">
                  {extractArticleBody(article).substring(0, 150)}...
                </p>
              </div>
            ))}
          </div>
        </section>
        {/* Overview Modal */}
        {showOverviewModal && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={handleCloseOverviewModal}
          >
            <div
              ref={overviewModalRef}
              className={`bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg w-11/12 md:w-3/4 lg:w-1/2 max-h-[90vh] overflow-y-auto relative p-6 ${
                closingOverview ? "animate-fadeOut" : "animate-fadeIn"
              }`}
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="absolute top-2 right-2 text-gray-400 hover:text-white text-xl transition-shadow duration-300 hover:shadow-xl"
                onClick={handleCloseOverviewModal}
              >
                &times;
              </button>
              <div
                className="prose dark:prose-invert max-w-none"
                dangerouslySetInnerHTML={{ __html: marked.parse(modalContent) }}
              />
              <div className="mt-6 flex justify-between items-center">
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
                  onClick={handleBackToTopOverview}
                >
                  Back to Top
                </button>
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
                  onClick={handleCloseOverviewModal}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
        {/* Old Article Modal */}
        {showArticleModal && selectedArticle && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={handleCloseArticleModal}
          >
            <div
              ref={articleModalRef}
              className={`bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg w-11/12 md:w-3/4 lg:w-1/2 max-h-[90vh] overflow-y-auto relative p-6 ${
                closingArticle ? "animate-fadeOut" : "animate-fadeIn"
              }`}
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="absolute top-2 right-2 text-gray-400 hover:text-white text-xl transition-shadow duration-300 hover:shadow-xl"
                onClick={handleCloseArticleModal}
              >
                &times;
              </button>
              <h2 className="text-2xl font-bold mb-4 text-blue-700 dark:text-blue-400">
                {extractArticleTitle(selectedArticle)}
              </h2>
              <div
                className="prose dark:prose-invert max-w-none"
                dangerouslySetInnerHTML={{
                  __html: marked.parse(processArticleContent(selectedArticle)),
                }}
              />
              <div className="mt-6 flex justify-between items-center">
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
                  onClick={handleBackToTopArticle}
                >
                  Back to Top
                </button>
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
                  onClick={handleCloseArticleModal}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
