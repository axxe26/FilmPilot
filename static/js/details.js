document.addEventListener("DOMContentLoaded", () => {

    // Carrusel 
    document.querySelectorAll(".carousel-wrapper").forEach(wrapper => {

        const carousel = wrapper.querySelector(".carousel");
        const leftArrow = wrapper.querySelector(".left-arrow");
        const rightArrow = wrapper.querySelector(".right-arrow");

        if (rightArrow) {
            rightArrow.addEventListener("click", () => {
                carousel.scrollBy({ left: 300, behavior: "smooth" });
            });
        }

        if (leftArrow) {
            leftArrow.addEventListener("click", () => {
                carousel.scrollBy({ left: -300, behavior: "smooth" });
            });
        }
    });


    // Acordeon temporadas
    document.querySelectorAll(".season-header").forEach(header => {

        header.addEventListener("click", async () => {

            const seasonNumber = header.dataset.season;
            const container = document.getElementById(`season-${seasonNumber}`);

            const isOpen = container.classList.contains("show");

            if (isOpen) {
                container.classList.remove("show");
                header.classList.remove("active");
                return;
            }

            header.classList.add("active");

            if (container.innerHTML.trim() === "") {

                try {
                    const response = await fetch(`/tv/${TMDB_ID}/season/${seasonNumber}/`);

                    if (!response.ok) {
                        console.error("Error al cargar episodios:", response.status);
                        return;
                    }

                    const episodes = await response.json();

                    container.innerHTML = episodes.map(ep => `
                        <div class="episode">
                            <img
                                src="${
                                    ep.still_path
                                        ? `https://image.tmdb.org/t/p/w300${ep.still_path}`
                                        : "/static/images/default_episode.jpg"
                                }"
                                alt="Episode ${ep.episode_number}"
                            >
                            <div class="episode-info">
                                <h4>Episode ${ep.episode_number}</h4>
                                <p class="episode-title">${ep.name || "Untitled"}</p>
                                <p class="episode-description">${ep.overview || "No description available."}</p>
                                <span>${ep.runtime ? ep.runtime + " min" : ""}</span>
                                <button
                                    class="episode-watch-btn"
                                    data-season="${seasonNumber}"
                                    data-episode="${ep.episode_number}"
                                >
                                    Mark as watched
                                </button>
                            </div>
                        </div>
                    `).join("");

                    // Verificar si la temporada completa está marcada
                    const seasonRes = await fetch(`/check_season/${TMDB_ID}/${seasonNumber}/`);
                    const seasonData = await seasonRes.json();

                    if (seasonData.watched) {
                        container.querySelectorAll(".episode-watch-btn").forEach(btn => {
                            btn.classList.add("watched");
                            btn.textContent = "Watched";
                        });
                    } else {
                        const episodeBtns = container.querySelectorAll(".episode-watch-btn");

                        episodeBtns.forEach(async (btn) => {
                            const season = btn.dataset.season;
                            const episode = btn.dataset.episode;

                            try {
                                const res = await fetch(`/check_episode/${TMDB_ID}/${season}/${episode}/`);
                                if (!res.ok) return;

                                const data = await res.json();

                                btn.classList.toggle("watched", data.watched);
                                btn.textContent = data.watched ? "Watched" : "Mark as watched";
                            } catch (err) {
                                console.error("check_episode error:", err);
                            }
                        });
                    }

                } catch (error) {
                    console.error("Error fetching season:", error);
                }
            }

            container.classList.add("show");
        });
    });


    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="));
        return cookieValue ? cookieValue.split("=")[1] : "";
    }


    // Toggle Episodios 
    document.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("episode-watch-btn")) return;

        const btn = e.target;

        const res = await fetch("/toggle_episode/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                tmdb_id: TMDB_ID,
                season_number: btn.dataset.season,
                episode_number: btn.dataset.episode,
                title: document.querySelector(".title").textContent.trim(),
                poster_path: document.querySelector(".poster").getAttribute("src")
                    .replace("https://image.tmdb.org/t/p/w500", "")
            })
        });

        const data = await res.json();
        btn.classList.toggle("watched", data.watched);
        btn.textContent = data.watched ? "Watched" : "Mark as watched";
    });


    // Toggle temporadas
    let seasonToggling = false;

    document.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("watch-season-btn")) return;

        e.stopPropagation();

        if (seasonToggling) return;
        seasonToggling = true;

        const btn = e.target;
        const episodeCount = parseInt(btn.dataset.episodes);
        const seasonNumber = btn.dataset.season;

        if (!episodeCount || episodeCount === 0) {
            seasonToggling = false;
            return;
        }

        const res = await fetch("/toggle_season/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                tmdb_id: TMDB_ID,
                season_number: seasonNumber,
                episode_count: episodeCount,
                title: document.querySelector(".title").textContent.trim(),
                poster_path: document.querySelector(".poster").getAttribute("src")
                    .replace("https://image.tmdb.org/t/p/w500", "")
            })
        });

        const data = await res.json();

        btn.classList.toggle("watched", data.watched);
        btn.textContent = data.watched ? "Season watched" : "Watched season";

        // actualizar solo si ya están abiertos
        document.querySelectorAll(`.episode-watch-btn[data-season="${seasonNumber}"]`)
            .forEach(epBtn => {
                epBtn.classList.toggle("watched", data.watched);
                epBtn.textContent = data.watched ? "Watched" : "Mark as watched";
            });

        seasonToggling = false;
    });

    const movieBtn = document.querySelector(".watch-movie-btn");
    if (movieBtn) {
        (async () => {
            const res = await fetch(`/check_movie/${TMDB_ID}/`);
            const data = await res.json();
            const btn = document.querySelector(".watch-movie-btn");
            if (!btn) return;
            btn.classList.toggle("watched", data.watched);
            btn.textContent = data.watched ? "Movie watched" : "To Watch";
        })();
    }


    // Toggle peliculas
    document.addEventListener("click", async (e) => {
        if (!e.target.classList.contains("watch-movie-btn")) return;

        const btn = e.target;

        const res = await fetch("/toggle_movie/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                tmdb_id: TMDB_ID,
                title: document.querySelector(".title").textContent.trim(),
                poster_path: document.querySelector(".poster").getAttribute("src")
                    .replace("https://image.tmdb.org/t/p/w500", "")
            })
        });

        const data = await res.json();
        btn.classList.toggle("watched", data.watched);
        btn.textContent = data.watched ? "Movie watched" : "To Watch";
    });
    
    // Check temporada
    document.querySelectorAll(".watch-season-btn").forEach((btn) => {
        const season = btn.dataset.season;

        if (!season) {
            console.error("Season undefined boton:", btn);
            return;
        }

        (async () => {
            try {
                const res = await fetch(`/check_season/${TMDB_ID}/${season}/`);
                if (!res.ok) return;
                const data = await res.json();
                btn.classList.toggle("watched", data.watched);
                btn.textContent = data.watched ? "Season watched" : "Watched season";
            } catch (err) {
                console.error("Error check_season:", err);
            }
        })();
    });


    // Rating
    const stars = document.querySelectorAll(".star");
    let selectedRating = window.USER_RATING || 0;

    highlightStars(selectedRating);

    stars.forEach(star => {
        star.addEventListener("click", () => {
            selectedRating = parseInt(star.dataset.value);
            highlightStars(selectedRating);

            fetch("/save_rating/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    tmdb_id: parseInt(window.TMDB_ID),
                    media_type: window.MEDIA_TYPE,
                    value: selectedRating,
                    title: document.querySelector(".title").textContent.trim(),
                    poster_path: document.querySelector(".poster").getAttribute("src")
                })
            })
            .then(res => res.json())
            .then(data => console.log("Rating guardado:", data))
            .catch(err => console.error("Error guardando rating:", err));
        });
    });

    function highlightStars(value) {
        stars.forEach(star => {
            const starValue = parseInt(star.dataset.value);
            star.classList.toggle("active", starValue <= value);
        });
    }


    // WatchList
    document.querySelectorAll(".watch-list-btn").forEach(async btn => {
        const icon = btn.querySelector(".watchlist-icon");

        const checkRes = await fetch(`/check_watchlist/${window.TMDB_ID}/${window.MEDIA_TYPE}/`);
        const checkData = await checkRes.json();
        icon.src = checkData.saved
            ? "/static/img/watchlist-active-icon.png"
            : "/static/img/watchlist-inactive-icon.png";

        btn.addEventListener("click", async () => {
            const res = await fetch("/toggle_watchlist/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    tmdb_id: parseInt(window.TMDB_ID),
                    media_type: window.MEDIA_TYPE,
                    title: document.querySelector(".title").textContent.trim(),
                    poster_path: document.querySelector(".poster").getAttribute("src")
                        .replace("https://image.tmdb.org/t/p/w500", "")
                })
            });

            const data = await res.json();
            icon.src = data.saved
                ? "/static/img/watchlist-active-icon.png"
                : "/static/img/watchlist-inactive-icon.png";
        });
    });


    // Favoritos
    document.querySelectorAll(".favorites-btn").forEach(async btn => {
        const icon = btn.querySelector(".favorite-icon");

        const checkRes = await fetch(`/check_favorites/${window.TMDB_ID}/${window.MEDIA_TYPE}/`);
        const checkData = await checkRes.json();
        icon.src = checkData.saved
            ? "/static/img/favorite-active-icon.png"
            : "/static/img/favorite-inactive-icon.png";

        btn.addEventListener("click", async () => {
            const res = await fetch("/toggle_favorites/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    tmdb_id: parseInt(window.TMDB_ID),
                    media_type: window.MEDIA_TYPE,
                    title: document.querySelector(".title").textContent.trim(),
                    poster_path: document.querySelector(".poster").getAttribute("src")
                        .replace("https://image.tmdb.org/t/p/w500", "")
                })
            });

            const data = await res.json();
            icon.src = data.saved
                ? "/static/img/favorite-active-icon.png"
                : "/static/img/favorite-inactive-icon.png";
        });
    });

});