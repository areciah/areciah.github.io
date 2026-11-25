(() => {
  const filters = document.getElementById('archive-filters');
  const category = document.getElementById('archive-category');
  const tag = document.getElementById('archive-tag');
  const order = document.getElementById('archive-order');
  const list = document.getElementById('archive-list');
  const count = document.getElementById('archive-count');
  const posts = Array.from(list.children, row => ({
    row,
    tags: JSON.parse(row.dataset.tags) || [],
    categories: JSON.parse(row.dataset.categories)
  }));

  function update() {
    const uncategorized = category.selectedOptions[0].hasAttribute('data-uncategorized');
    const visible = posts.filter(post => (!tag || !tag.value || post.tags.includes(tag.value)) && (uncategorized
      ? post.categories.length === 0
      : !category.value || post.categories.includes(category.value)));
    if (order.value === 'oldest') visible.reverse();
    list.replaceChildren(...visible.map(post => post.row));
    count.textContent = '글 ' + visible.length + '편';
  }

  filters.addEventListener('change', update);
  update();
  filters.hidden = false;
})();
