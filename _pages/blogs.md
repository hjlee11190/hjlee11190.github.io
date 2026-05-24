---
layout: archive
permalink: /blogs/
title: "Blogs"
author_profile: true
---

{% include base_path %}

{% assign sorted_blogs = site.blogs | sort: "date" | reverse %}
{% for post in site.blogs reversed %}
  {% include archive-single.html %}
{% endfor %}
