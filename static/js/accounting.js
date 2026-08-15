$(function () {
    $('.jalali-date').persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        initialValue: false,
        observer: true,
        calendar: {
            persian: {
                locale: 'fa'
            }
        },
        navigator: {
            enabled: true
        },
        toolbox: {
            enabled: true,
            calendarSwitch: {
                enabled: false
            }
        }
    });
});
