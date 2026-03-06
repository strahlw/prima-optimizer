export function useCollapse() {
    function enter(el: Element, done: () => void) {
        const element = el as HTMLElement;
        element.style.maxHeight = '0';
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition =
                'max-height 0.1s ease-in-out, padding 0.1s ease-in-out, opacity 0.2s ease-in-out';
            element.style.maxHeight = el.scrollHeight + 'px';
            element.style.opacity = '1';
            element.addEventListener('transitionend', done, { once: true });
        });
    }

    function leave(el: Element, done: () => void) {
        const element = el as HTMLElement;
        element.style.maxHeight = el.scrollHeight + 'px';
        setTimeout(() => {
            element.style.maxHeight = '0';
            element.addEventListener('transitionend', done, { once: true });
        });
    }

    return { enter, leave };
}
