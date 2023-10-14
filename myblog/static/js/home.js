const trendContainer = document.getElementById("trend-container");

const pageHeight = document.documentElement.scrollHeight;
const windowHeight = window.innerHeight;

const visibleHeight = pageHeight - windowHeight;

function isNearBottom() {
  const scrollPosition = window.scrollY || document.documentElement.scrollTop;
  const visibleHeight =
    window.innerHeight || document.documentElement.clientHeight;
  const totalHeight = document.documentElement.scrollHeight;
  const distanceToBottom = totalHeight - (scrollPosition + visibleHeight);

  // 判断滚动位置是否接近底部
  return distanceToBottom < 50; // 可根据需要调整阈值
}

// 函数节流
let throttleTimer = null;
const throttleDelay = 1000; // 设置节流的延迟时间，单位为毫秒

window.addEventListener("scroll", function () {
  if (!throttleTimer) {
    throttleTimer = setTimeout(function () {
      throttleTimer = null;
      if (isNearBottom()) {
        addTrends();
      }
    }, throttleDelay);
  }
});

// 触发的函数
function addTrends() {
  const cardElements = document.querySelectorAll(".card-item");
  const lastCardElement = cardElements[cardElements.length - 1];
  const lastChildDate = lastCardElement.getAttribute("data-date");
  if (lastChildDate) {
    const url = `/trend?before=${lastChildDate}`;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        if (data) {
          data.forEach((item) => {
            const card = document.createElement("div");
            card.classList.add("card", "mb-3", "card-item");
            card.setAttribute("data-date", item.date);

            const cardHeader = document.createElement("div");
            cardHeader.classList.add("card-header", "font-italic");
            const small = document.createElement("small");
            const data_1 = `${item.date} ${item.author} 发布在 ${item.repo_name}`;
            small.textContent = data_1;
            cardHeader.appendChild(small);
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.classList.add("card-body");
            const h5 = document.createElement("h5");
            h5.classList.add("card-title");
            h5.textContent = item.summary;
            const p = document.createElement("p");
            p.classList.add("card-text");
            p.textContent = item.body;
            cardBody.appendChild(h5);
            cardBody.appendChild(p);
            card.appendChild(cardBody);

            trendContainer.appendChild(card);
          });
        }
      })
      .catch((error) => {
        console.error("请求数据时发生错误:", error);
      });
  }
}
