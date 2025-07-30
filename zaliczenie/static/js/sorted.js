document.addEventListener('DOMContentLoaded', function () {
    const sortedSelect = document.getElementById('sorted');
    if (sortedSelect) {
        sortedSelect.addEventListener('change', function () {
            const sortValue = this.value;
            const url = new URL(window.location);
            url.searchParams.set('sorted', sortValue);
            window.location.href = url.toString();
        });
    }
});
