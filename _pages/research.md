---
layout: archive
title: "Research"
permalink: /research/
author_profile: true
---

{% include base_path %}

{% assign sorted_blogs = site.blogs | sort: "date" | reverse %}
{% for post in site.research %}
  {% include archive-single.html %}
{% endfor %}



