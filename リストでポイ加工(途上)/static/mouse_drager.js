function () {
    'use strict';

    const ddBox = document.querySelector('.dd-box');
    const ddBoxList = ddBox.querySelectorAll('li');
    let data = {
        target: null,
        diffX: 0,
        diffY: 0,
    };
    const util = {
        index(el) {
            const parent = el.parentElement;
            const siblings = parent.children;
            const siblingsArr = [].slice.call(siblings);
            const idx = siblingsArr.indexOf(el);

            return idx;
        },
        insertClone(target, insertIdx) {
            const cloneName = `ddItemClone_${Math.trunc(Math.random() * 10000)}`;
            const clone = target.cloneNode(true);
            const parent = target.parentElement;
            const siblings = parent.children;

            clone.classList.add('hidden');
            clone.classList.add(cloneName);
            siblings[insertIdx].insertAdjacentElement('afterend', clone);

            return cloneName;
        },
        swap(target) {
            const selfIdx = util.index(target);
            const cloneIdx = selfIdx + 1;
            const parent = target.parentElement;
            const siblings = parent.querySelectorAll(`:scope > *:not(.onGrab):not(.${data.cloneName})`);

            for (let thatIdx = 0, len = siblings.length; thatIdx < len; thatIdx++) {
                const targetW = target.offsetWidth;
                const targetH = target.offsetHeight;
                const targetRect = target.getBoundingClientRect();
                const targetRectX = targetRect.left;
                const targetRectY = targetRect.top;
                const that = siblings[thatIdx];
                const thatW = that.offsetWidth;
                const thatH = that.offsetHeight;
                const thatRect = that.getBoundingClientRect();
                const thatRectX = thatRect.left;
                const thatRectY = thatRect.top;
                const thatRectYHalf = thatRectY + (thatH / 2);
                const hitX = thatRectX <= (targetRectX + targetW) && thatRectX + thatW >= targetRectX;
                const hitY = targetRectY <= thatRectYHalf && (targetRectY + targetH) >= thatRectYHalf;
                const isHit = hitX && hitY;

                if (isHit) {
                    const siblingsAll = parent.children;
                    const clone = siblingsAll[cloneIdx];

                    parent.insertBefore(clone, selfIdx > thatIdx ? that : that.nextSibling);
                    parent.insertBefore(target, clone);

                    break;
                }
            }
        }
    };
    const ev = {
        down(e) {
            const target = e.target;
            const pageX = e.pageX;
            const pageY = e.pageY;
            const targetW = target.offsetWidth;
            const targetRect = target.getBoundingClientRect();
            const targetRectX = targetRect.left;
            const targetRectY = targetRect.top;

            data.target = target;
            data.diffX = pageX - targetRectX;
            data.diffY = pageY - targetRectY;
            data.cloneName = util.insertClone(target, util.index(target));
            target.style.width = `${targetW}px`;
            target.classList.add('onGrab');
            window.addEventListener('mousemove', ev.move);
            window.addEventListener('mouseup', ev.up);
        },
        move(e) {
            const target = data.target;
            const pageX = e.pageX;
            const pageY = e.pageY;
            const targetPosL = pageX - data.diffX;
            const targetPosT = pageY - data.diffY;

            target.style.left = `${targetPosL}px`;
            target.style.top = `${targetPosT}px`;
            util.swap(target);
        },
        up() {
            const target = data.target;
            const cloneSelector = `.${data.cloneName}`;
            const clone = document.querySelector(cloneSelector);

            data.cloneName = '';
            clone.remove();
            target.removeAttribute('style');
            target.classList.remove('onGrab');
            target.classList.remove('onDrag');
            window.removeEventListener('mousemove', ev.move);
            window.removeEventListener('mouseup', ev.up);
        }
    };

    ddBoxList.forEach((el) => {
        el.addEventListener('mousedown', ev.down);
    });
}());