document.addEventListener("DOMContentLoaded", () => {
  const ytVideos = document.querySelectorAll(".yt-video");

  ytVideos.forEach((container) => {
    const videoId = container.getAttribute("data-video-id");
    const thumbnailWrapper = container.querySelector(".yt-thumbnail-wraper");

    if (!videoId || !thumbnailWrapper) return;

    thumbnailWrapper.addEventListener("click", () => {
      const iframe = document.createElement("iframe");
      iframe.setAttribute(
        "src",
        `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`,
      );
      iframe.setAttribute("title", "YouTube video player");
      iframe.setAttribute("frameborder", "0");
      iframe.setAttribute(
        "allow",
        "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
      );
      iframe.setAttribute("allowfullscreen", "");
      iframe.setAttribute("class", "w-full h-full");

      // Vyčistíme wrapper a vložíme iframe
      thumbnailWrapper.innerHTML = "";
      thumbnailWrapper.appendChild(iframe);

      // Odstraníme kurzor pointer, jelikož už tam je iframe
      thumbnailWrapper.classList.remove("cursor-pointer", "group");
    });
  });
});
