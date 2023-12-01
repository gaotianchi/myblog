**Project name**: MYBLOG   

**Introduction**: MYBLOG is a personal blog website. Like many personal blog websites, authors can publish articles on it and visitors can leave messages under the articles.   

**Features**: MYBLOG uses the GIT HOOKS POST-RECEIVE feature to implement a convenient article publishing function. Specifically, the author uses the MARKDOWN editor to write the article locally, and then uses GIT to submit it to the remote warehouse after completion. MYBLOG will read it after the PUSH is completed. The article content in the remote working directory is then rendered into HTML text and stored in the database. At the same time, other metadata changes will also be updated in the database. This helps authors focus on writing locally without having to log into the website to write articles.