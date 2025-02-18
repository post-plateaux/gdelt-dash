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
  // Default darkMode to true for all visitors
  const [darkMode, setDarkMode] = useState<boolean>(true);

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
  const [currentPage, setCurrentPage] = useState<number>(1);
  const articlesPerPage = 12;
  const indexOfLastArticle = currentPage * articlesPerPage;
  const indexOfFirstArticle = indexOfLastArticle - articlesPerPage;
  const currentOldArticles = oldArticles.slice(indexOfFirstArticle, indexOfLastArticle);
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
      const response = await fetch("content/article.md");
      if (!response.ok) throw new Error("Failed to fetch article.md");
      const text = await response.text();
      setLatestArticle(text);
    } catch (err) {
      console.error("Error fetching article.md:", err);
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

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(protocol + '://' + window.location.host + '/ws');
    socket.onmessage = (event) => {
      if (event.data === "article updated" || event.data === "article_update") {
        fetchLatestArticle();
        fetchOldArticles();
      }
    };
    return () => socket.close();
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
    <div className="min-h-screen bg-[#5D6D7E] text-gray-900 flex justify-center p-4 dark:bg-gray-900 dark:text-gray-100">
      {/* Scroll Progress Indicator */}
      <div className="fixed top-0 left-0 z-50">
        <div className="h-1 bg-blue-500" style={{ width: `${scrollProgress}%` }} />
      </div>
      <div className="max-w-4xl w-full bg-[#EBEDEF] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-lg pt-16 pr-6 pb-6 pl-6 relative">
        {/* Dark mode toggle */}
        <div className="absolute top-8 left-4">
          <button
            className="bg-gray-700 hover:bg-gray-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
            onClick={toggleDarkMode}
          >
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
        {/* About this Project button */}
        <div className="absolute top-8 right-4">
          <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-3 rounded transition-shadow duration-300 hover:shadow-xl"
            onClick={() => setShowOverviewModal(true)}
          >
            About this Project
          </button>
        </div>
        {/* Top Banner */}
        <div className="mt-4 mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          <iframe className="w-full" src="https://fifteen.postplateaux.com/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=9&__feature.dashboardSceneSolo" height="200" frameborder="0"></iframe>
          <iframe className="w-full" src="https://fifteen.postplateaux.com/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=8&__feature.dashboardSceneSolo" height="200" frameborder="0"></iframe>
        </div>
        {/* Overview Section */}
        <section className="mt-8">
          <h2 className="text-2xl font-bold mb-2 text-center text-blue-700 dark:text-blue-400">
            15 Every 15
          </h2>
          <p className="text-2xl font-bold mb-2 text-center text-blue-700 dark:text-blue-400">
            Translating 15 International Reports on the U.S. Every 15 Minutes
          </p>
          <div
            className="prose dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: marked.parse(overviewContent) }}
          />
        </section>
        {/* Additional Visualizations Section */}
        <section className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <iframe className="w-full" src="https://fifteen.postplateaux.com/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=1&__feature.dashboardSceneSolo" height="200" frameborder="0"></iframe>
            <iframe className="w-full" src="https://fifteen.postplateaux.com/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=2&__feature.dashboardSceneSolo" height="200" frameborder="0"></iframe>
          </div>
          
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <iframe className="w-full" src="https://fifteen.postplateaux.com/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=5&__feature.dashboardSceneSolo" height="200" frameborder="0"></iframe>
            <iframe className="w-full" src="https://fifteen.postplateaux.com/grafana/d-solo/ee25sajexuupsc/gdelt?orgId=1&timezone=browser&panelId=6&__feature.dashboardSceneSolo" height="200" frameborder="0"></iframe>
          </div>
          
          </section>
        {/* Divider with a visual element */}
        <div className="my-8 flex items-center">
          <hr className="flex-grow border-t border-gray-700" />
          <div className="mx-4">
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
          </div>
          <hr className="flex-grow border-t border-gray-700" />
        </div>
        {/* Old Articles Section */}
        <section className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-center text-blue-400">
            Previous Entries
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {currentOldArticles.map((article, index) => (
              <div
                key={index}
                className="bg-[#EBEDEF] dark:bg-gray-700 text-gray-900 dark:text-gray-300 rounded-lg p-4 cursor-pointer hover:bg-[#D3D3D3] dark:hover:bg-gray-600 transform hover:scale-105 transition-all duration-300"
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
          <div className="flex justify-center mt-4 space-x-4">
            {currentPage > 1 && (
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
              >
                Previous
              </button>
            )}
            {indexOfLastArticle < oldArticles.length && (
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded"
              >
                Next
              </button>
            )}
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
              className={`bg-[#EBEDEF] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg w-11/12 md:w-3/4 lg:w-1/2 max-h-[90vh] overflow-y-auto relative p-6 ${
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
              className={`bg-[#EBEDEF] dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg w-11/12 md:w-3/4 lg:w-1/2 max-h-[90vh] overflow-y-auto relative p-6 ${
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
