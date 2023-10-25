// 职责：当用户页面到达底部的时候加载更多的 trend 数据

const trendContainer = document.getElementById("trends-container");

function isNearBottom() {
  const scrollPosition = window.scrollY || document.documentElement.scrollTop;
  const visibleHeight =
    window.innerHeight || document.documentElement.clientHeight;
  const totalHeight = document.documentElement.scrollHeight;
  const distanceToBottom = totalHeight - (scrollPosition + visibleHeight);

  return distanceToBottom < 50; //
}

let throttleTimer = null;
const throttleDelay = 1000;

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

function addTrends() {
  console.log("已经到达底部！！！");
  const cards = trendContainer.querySelectorAll(".card");
  const lastCard = cards[cards.length - 1];
  const lastCardId = lastCard.getAttribute("data-trendid");
  if (!lastCardId) {
    console.log("还没有任何动态");
    return;
  }

  const trendsUrl = `/trend?start_id=${lastCardId - 1}`;
  fetch(trendsUrl)
    .then((response) => response.json())
    .then((data) => {
      if (!data) {
        console.log("已经加载完全部动态");
        return;
      }
      data.forEach((trend) => {
        console.log(trend);
        const card = createCard(trend);
        trendContainer.appendChild(card);
      });
    });
}

function createCard(trend) {
  const card = document.createElement("div");
  card.setAttribute("class", "card mb-3");
  card.setAttribute("data-trendid", trend.id);
  const cardBody = document.createElement("div");
  cardBody.setAttribute("class", "card-body");
  const cardTitle = document.createElement("h4");
  cardTitle.setAttribute("class", "card-title");
  cardTitle.textContent = trend.title;
  const cardText = document.createElement("div");
  cardText.setAttribute("class", "card-text");
  cardText.textContent = trend.body;
  cardBody.appendChild(cardTitle);
  cardBody.appendChild(cardText);
  const cardFooter = document.createElement("div");
  cardFooter.setAttribute("class", "card-footer text-muted");
  const footerText = `${trend.time} 发布在 ${trend.project}`;
  cardFooter.textContent = footerText;
  card.appendChild(cardBody);
  card.appendChild(cardText);

  return card;
}
