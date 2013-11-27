/**
 * \file www/js/dynamic.js
 * \author Yankel Scialom (YSC) <yankel.scialom@mail.com>
 *
 * This file update a specialy-formed HTML table to add:
 * \li a way to sort its columns;
 * \li a way to filter the table lines;
 * \li a dynamic pagination system.
 *
 * It requires:
 * \li jQuery 2.0.3 (earlier version not tested);
 * \li jQuery-ui 1.10.3 (earlier version not tested);
 * \li jQuery TableSorter;
 * \li jQuery SimplePagination;
 * \li Class.js;
 * \li PersistJS.
 */
/**
 * \class MasterFilter
 * \brief Filters the table using \ref AbstractFilters.
 */
var MasterFilter = Class.extend({
    /**
     * \property priv_initialized
     * \brief Is the object initialized.
     */
    priv_initialized: false,
    /**
     * \property priv_rows_per_page
     * \brief Number of rows per page.
     */
    priv_rows_per_page: offers_per_page,
    /**
     * \property filters
     * \brief Filters to use.
     */
    priv_filters: null,
    /**
     * \fn priv_get_next_rows()
     * \brief Get the next rows according to the number of rows per page.
     * \see priv_rows_per_page
     */
    priv_get_next_rows: function() {
        var first = this.priv_next_row;
        this.priv_next_row += this.priv_rows_per_page;
        if (0 == first)
            return $("#offers > tbody > tr:lt(" + this.priv_rows_per_page + ")");
        return $("#offers > tbody > tr:gt(" + first + "):lt(" + this.priv_rows_per_page + ")");
    },
    /**
     * \fn priv_set_visibility(row, show)
     * \brief Set the visibility of a row.
     */
    priv_set_visibility: function(row, show) {
        if (show) {
            $(row).show();
        } else {
            $(row).hide();
        }
    },
    /**
     * \fn priv_get_visibility(row)
     * \brief Get the visibility of a row.
     */
    priv_get_visibility: function(row) {
        return "none" != $(row).css("display");
    },
    /**
     * \fn priv_apply_on_row(row, source = null)
     * \brief Apply the filters on a row.
     */
    priv_apply_on_row: function(row, source) {
		if (undefined === source)
			source = null;
        var self = this;
        var accepted = true;
        var test_value = function(filter, row) {
            var classname = filter.classname();
            var value = $(row).find("." + classname).text();
            return filter.test(value);
        };
        if (null == source) {
            $.each(self.filters, function(key, filter) {
                if (! test_value(filter, row)) {
                    accepted = false;
                    return false;
                }
            });
        } else {
            accepted = test_value(source, row);
            var cur_visibility = this.priv_get_visibility(row);
            if (cur_visibility ^ accepted) {
                return this.priv_apply_on_row(row);
            }
        }
        this.priv_set_visibility(row, accepted);
        return accepted;
    },
    /**
     * \property priv_page_first_indexes
     * \brief Hashmap caching the index of the first row of each page.
     */
    priv_page_first_indexes: new Array(),
    /**
     * \property priv_next_row
     * \brief Index of next row to be returned by priv_get_next_rows()
     * \see priv_get_next_rows()
     */
    priv_next_row: 0,
    /**
     * \property priv_navbar
     * \brief Navigation bar as NavigationBar object.
     * \see NavigationBar
     */
    priv_navbar: null,
    /**
     * \fn priv_show_page(page, source = null)
     * \brief Show page number \a page.
     */
    priv_show_page: function(page, source) {
		if (undefined === source)
				source = null;
        var self = this;

        // pagination initialization
        if (0 == page  || undefined === this.priv_page_first_indexes[page]) {
            this.priv_page_first_indexes = new Array();
            this.priv_page_first_indexes[0] = 0;
            this.priv_next_row = 0;
            this.priv_navbar.set_page_count(1);
        }

        // Get page's first row index
        this.priv_next_row = this.priv_page_first_indexes[page];        

        // Test rows from page's first until page full or no more rows
        var rows_cnt = 0;
        $("#offers > tbody > tr:visible").each(function(key, row) {
            self.priv_set_visibility(row, false);
        });
        do {
            var $rows = this.priv_get_next_rows();
            if (0 == $rows.length) {
                this.priv_navbar.set_page_count(page+1);
                break;
            }
            $rows.each(function(key, row) {
                if (rows_cnt < self.priv_rows_per_page) {
                    if (self.priv_apply_on_row(row, source)) {
                        rows_cnt++;
                    }
                } else {
                    self.priv_next_row -= self.priv_rows_per_page - key;
                    return false;
                }
            });
        } while (rows_cnt < this.priv_rows_per_page);

        // Save next page's first row
        if (this.priv_next_row >= this.priv_page_first_indexes[page])
            this.priv_page_first_indexes[page+1] = this.priv_next_row;
        else
            rows_cnt = -1;

        if (rows_cnt == this.priv_rows_per_page)
            this.priv_navbar.acknoledge_page(page+1);
    },
    /**
     * \fn init()
     * \brief Constructor.
     * \see add_filter(filter)
     *
     * Creates and inserts DOM elements providing a filter on the table.
     */
    init: function() {
        var self = this;
        this.filters = new Array();
        new PubdateFilter("pubdate", this).attach(
            $("#lineFilters > .pubdate")
        );
        new TitleFilter("title", this).attach(
            $("#lineFilters > .title")
        );
        new CompanyFilter("company", this).attach(
            $("#lineFilters > .company")
        );
        new LocationFilter("location", this).attach(
            $("#lineFilters > .location")
        );
        new ContractFilter("contract", this).attach(
            $("#lineFilters > .contract")
        );
        new SalaryFilter("salary", this).attach(
            $("#lineFilters > .salary")
        );
        new SourceFilter("source", this).attach(
            $("#lineFilters > .source")
        );
        this.priv_navbar = new NavigationBar({
            change: function(page) {
                self.priv_show_page(page);
            }
        });
        this.priv_navbar.attach(
            $("<p>", {id: "pagination_bar_root"}).appendTo("body > nav > div")
        );
        this.priv_initialized = true;
        this.apply();
    },
    /**
     * \fn add_filter(filter)
     * \brief Adds the \ref AbstractFilter \a filter.
     */
    add_filter: function(filter) {
        this.filters = this.filters.concat(filter);
    },
    /**
     * \fn apply(source = null)
     * \brief Applies the filters' selections and filters the table.
     * \param[in] source The filter to update or \c null to apply all filters.
     */
    apply: function(source) {
		if (undefined === source)
			source = null;
        // source no more used.
        if (!this.priv_initialized)
            return;
        this.priv_navbar.set_page(0);
    }
});

/**
 * \class NavigationBar
 * \brief The navigation bar to let the user change pages.
 */
var NavigationBar = Class.extend({
    /**
     * \property priv_current_page
     * \brief Displayed page.
     */
    priv_current_page: 0,
    priv_total_pages: 1,
    /**
     * \property priv_bar
     * \brief navigation bar as a jQuery object..
     */
    priv_bar: null,
    priv_nth_link: function(nth) {
        var $lis = this.priv_bar.children();
        if (0 <= nth && nth < $lis.length)
            return $($lis[nth]);
        console.error("NavigationBar.priv_nth_link(" + nth + "): index out of range.");
        return null;
    },
    priv_on_change: null,
    redraw: function() {
        var self = this;
        /* Prev */
        var $prev = self.priv_nth_link(0);
        if (self.priv_current_page <= 0)
            $prev.addClass("disabled");
        else
            $prev.removeClass("disabled");
        /* current */
        self.priv_nth_link(1).children("a").text(self.priv_current_page+1);
        /* Next */
        var $next = this.priv_nth_link(2);
        if (self.priv_current_page >= self.priv_total_pages-1)
            $next.addClass("disabled");
        else
            $next.removeClass("disabled");
    },
    /**
     * \fn init(options = null)
     * \brief COnstructor.
     */
    init: function(options) {
        var self = this;
		var options = $.extend({
			change: function(page) {}
		}, options || {} );

        /* save callback */
        self.priv_on_change = options.change;

        /* insert pagination bar */
        this.priv_bar = $("<ul>")
            .addClass("navbar-right")
            .addClass("pagination");
        var mklink = function(key, opt) {
            var opt = $.extend({
                html: "-",
                active: false,
                disabled: false
            }, opt || {} );
            var $link = $("<a>", {href: "#"})
                .html(opt.html)
                .click(function() {
                    opt.click();
                })
            var $result = $("<li>")
                .append($link);
            if (opt.active)
                $result.addClass("active");
            if (opt.disabled)
                $result.addClass("disabled");

            return $result;
        }
        var append_link = function(key, val) {
            self.priv_bar.append(mklink(key, val));
        }
        $.each([
            {html: "&laquo;", click: function() {
                self.set_page(self.priv_current_page-1);
            }},
            {html: 1, active: true},
            {html: "&raquo;", click: function() {
                self.set_page(self.priv_current_page+1);
            }}
        ], append_link);
    },
    /**
     * \fn attach(parent)
     * \brief Attach itself to \a parent.
     */
    attach: function(parent) {
        this.priv_bar.appendTo(parent);
    },
    /**
     * \fn set_page_count(page_count)
     * \brief Change total number of pages.
     */
    set_page_count: function(page_count) {
        if (page_count > 0 )
            this.priv_total_pages = page_count;
        else
            console.error("NavigationBar.set_page_count(" + page_count
            + "): page_count must be strictly positive.");
        this.redraw();
    },
    /**
     * \fn acknoledge_page(page_number)
     * \brief Acknoledge the existance of page number \a page_number.
     *
     * Increase the total number of pages if necessary.
     */
    acknoledge_page: function(page_number) {
        if (page_number >= this.priv_total_pages)
            this.set_page_count(page_number+1);
    },
    /**
     * \fn set_page(page_number)
     * \brief Set the current displayed page number.
     */
    set_page: function(page_number) {
        if (0 <= page_number && page_number < this.priv_total_pages)
            this.priv_current_page = page_number;
        else
            console.error("NavigationBar.set_page_count(" + page_number
            + "): page_count must be strictly positive.");
        this.redraw();
        this.priv_on_change(this.priv_current_page);
    }
});


/**
 * \class AbstractFilter
 * \brief Mother class of all filters.
 */
var AbstractFilter = Class.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     */
    priv_select_from_array: function(id, choices, options)  {
        options = $.extend({
            multiple: false,
            liveSearch: false,
            text: "{0} on {1}",
            width: "auto"
        }, options || {});
        var $result = $("<select>", {id: id})
            .addClass("selectpicker")
            .attr("data-width", options.width);
        if (options.multiple)
            $result
                .prop("multiple", "multiple")
                .attr("data-selected-text-format", "count > 1")
                .attr("data-count-selected-text", options.text);
        if (options.liveSearch)
            $result.attr("data-live-search", "true");
        $.each(choices, function(key, val) {
            var $elt = $("<option>");
            $elt.append(val);
            $result.append($elt);
        });
        return $result;
    },
    /**
     * \fn priv_textbox(id, filigran, buttons)
     * \brief Creates detached text box width buttons.
     */
    priv_textbox: function(id, filigran, callbacks, buttons) {
        /* container */
        var $div = $('<div class="input-group">');
        /* text bar */
        var $edit = $('<input type="text" class="form-control">')
            .prop("id", id)
            .attr("placeholder", filigran)
            .appendTo($div);
        var cbs = $.extend({
            click: function() {},
            keyup: function() {},
            keydown: function() {},
            change: function() {}
        }, callbacks || {});
        $edit.click(cbs.click);
        $edit.keyup(cbs.keyup);
        $edit.keydown(cbs.keydown);
        $edit.change(cbs.change);
        /* buttons */
        var $span = $('<span class="input-group-btn">')
            .appendTo($div);
        $.each(buttons, function(key, val) {
            var button = $.extend({
                text: "OK",
                click: function() {}
            }, val || {});
            var $button = $('<button class="btn btn-default" type="button">')
                .appendTo($span)
                .text(button.text)
                .click(button.click);
        });
        return $div;
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this.priv_classname = classname;
        this.priv_master_filter = master_filter;
        this.priv_master_filter.add_filter(this);
    },
    /**
     * \fn apply(source = null)
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     * \param[in] source The filter to update or \c null to apply all filters.
     */
    apply: function(source) {
        if (undefined !== this.priv_master_filter)
            this.priv_master_filter.apply(source);
    },
    /**
     * \property classname()
     * \returns The classname of the filter.
     */
    classname: function() { return this.priv_classname;},
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        return false;
    },
    /**
     * \fn test(value)
     * \brief Tests a \a value according to the filter.
     * \returns Either \c true of \c false.
     */
    test: function(value) {
        return true;
    }
});


/**
 * \class PubdateFilter
 * \brief Filter on publication date.
 */
var PubdateFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \property priv_selected_button_class_name
     * \brief Name of CSS class for the selected button.
     */
    priv_selected_button_class_name: "ui-my-selected-button",
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        /* button creation
         * <div id="filter_pubdate_box">
         *      <a id="filter_pubdate_before" class="filter_pubdate_buttons">Before</a>
         *      <a id="filter_pubdate_at" class="filter_pubdate_buttons">At</a>
         *      <a id="filter_pubdate_after" class="filter_pubdate_buttons">After</a>
         *      <div id="filter_pubdate_datepicker" />
         *  </div>
         */
        var $filter_pubdate_box = $("<div>", {id: "filter_pubdate_box"});
        var $filter_pubdate_before = $("<a>", {
            id: "filter_pubdate_before",
            class: "filter_pubdate_buttons"
        });
        var $filter_pubdate_at = $("<a>", {
            id: "filter_pubdate_at",
            class: "filter_pubdate_buttons"
        });
        var $filter_pubdate_after = $("<a>", {
            id: "filter_pubdate_after",
            class: "filter_pubdate_buttons"
        });
        var $filter_pubdate_datepicker = $("<div>", {id: "filter_pubdate_datepicker"});

        $filter_pubdate_before
            .text("Before")
            .button({
                icons: {primary: "ui-icon-circle-triangle-w"},
                text: false,
            })
            .appendTo($filter_pubdate_box);
        $filter_pubdate_at
            .text("At")
            .button()
            .appendTo($filter_pubdate_box);
        $filter_pubdate_after
            .text("After")
            .button({
                icons: {primary: "ui-icon-circle-triangle-e"},
                text: false,
            })
            .appendTo($filter_pubdate_box);
        $filter_pubdate_datepicker
            .appendTo($filter_pubdate_box);

        /* datepicker creation */
        $filter_pubdate_datepicker.datepicker({
            dateFormat: "yy-mm-dd",
            defaultDate: 0,
            onSelect: function(date_text, sender) {
                $filter_pubdate_at.find("span").text(date_text);
                $(this).hide();
                self.apply();
            }
        });
        var date_current = $.datepicker.formatDate(
            $filter_pubdate_datepicker.datepicker("option", "dateFormat"),
            $filter_pubdate_datepicker.datepicker("getDate")
        );
        $filter_pubdate_at.find("span").text(date_current);
        $filter_pubdate_at.mouseenter(function() {
            $filter_pubdate_datepicker.show();
        });
        $("#lineFilters ." + classname).mouseleave(function() {
            $filter_pubdate_datepicker.hide();
        });

        /* button picking */
        $filter_pubdate_box.find("a").click(function(e) {
            var class_checked = self.priv_selected_button_class_name;
            var $button = $("#" + e.currentTarget.id);
            $filter_pubdate_datepicker.hide();
            if ($button.hasClass(class_checked)) {
                $button.removeClass(class_checked)
            } else {
                $filter_pubdate_box.find("a").each(function(key, val) {
                    $(val).removeClass(class_checked);
                });
                $button.addClass(class_checked);
            }
            self.apply();
        });
        priv_elements = [$filter_pubdate_box];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        var self = this;
        $.each(priv_elements, function(key, val) {
            $parent.append(val);
        });
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the date \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        /* Find the selected button */
        var $selected_button = $(
            "#filter_pubdate_box a.filter_pubdate_buttons."
            + this.priv_selected_button_class_name
        );
        /* If there is no selected button, return true */
        if (undefined === $selected_button || null === $selected_button)
            return true;
        
        /* Get the selected button text */
        var text = $selected_button.text();
        if (undefined === text || null === text || "" === text)
            return true;
                
        /* Else, compare selected pubdate and offer pubdate */
        var date_format = $("#filter_pubdate_datepicker").datepicker("option", "dateFormat");
        var date_selected = $("#filter_pubdate_datepicker").datepicker("getDate");
        var date_selected_text = $.datepicker.formatDate(date_format, date_selected);
        if (undefined === date_selected || null == date_selected)
            return true;
        var date_offer = $.datepicker.parseDate(date_format, value);
        if (undefined === date_offer || null == date_offer)
            return true;
        switch(text)
        {
        case "Before":
            return date_selected >= date_offer;
        case date_selected_text:
            return Math.abs(date_selected - date_offer) < 1000*86400-1;
        case "After":
            return date_selected <= date_offer;
        default:
            console.error("Inconsistancy here. `text' value is `" + text + "'.");
            return true;
        }
    }
});


/**
 * \class TypeFilter
 * \brief Filter on Company type.
 */
var TypeFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var $filter_type_combobox = this.priv_select_from_array(
            "filter_type_pivot", ["All", "noSSII", "SSII"]
        );
        priv_elements = [$filter_type_combobox];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        var filter = this;
        $.each(priv_elements, function(key, val) {
            $parent.append(val);
        });
        priv_elements[0].change(function() {filter.apply();});
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the company type \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var pivot_type = $("#filter_type_pivot :selected").text();
        switch(pivot_type)
        {
        case "All":
            return true;
        case "noSSII":
        case "SSII":
            return value == pivot_type;
        default:
            console.error("Inconsistancy here. Must match <select> creation on init().");
            return true;
        }
    }
});


/**
 * \class TitleFilter
 * \brief Filter on the job description.
 */
var TitleFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var $filter_title_form = $("<form>")
            .addClass("form-search");
        var $filter_title = this.priv_textbox(
            "filter_title_text",
            "Coma-separated words",
            { keyup: function() { self.apply(); } },
            [
                {
                    text: "Clear",
                    click: function() {
                        $("#filter_title_text").val("");
                        self.apply();
                    }
                }
        ]).appendTo($filter_title_form);

        priv_elements = [$filter_title_form];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        var filter = this;
        $.each(priv_elements, function(key, val) {
            $parent.append(val);
        });
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job title \a value according GUI data.
     * \returns Either \c true of \c false.
     *
     * A search request can contain a coma-separated list of words. A job description
     * is considered valid if it matches at least one of the words.
     */
    test: function(value)  {
        var result = false;
        var pattern = $("#filter_title_text").val();
        if (undefined === pattern || 0 == pattern.length)
            return true;
        var patterns = pattern.split(/,\s*/);
        $.each(patterns, function(key, val) {
            if (0 != val.length && (new RegExp(val, "i")).test(value))
                return result = true;
        });
        return result;
    }
});


/**
 * \class CompanyFilter
 * \brief Filter on the company name.
 */
var CompanyFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \property priv_companies
     * \brief List of companies.
     */
     priv_companies: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var companies = [];
        $("#offers > tbody > tr > td." + self.classname()).each(function() {
            var company = $(this).text();
            if (-1 == $.inArray(company, companies))
                companies.push(company);
        });
        companies.sort();
        this.priv_companies = companies;

        var $filter_company_form = $("<form>")
            .addClass("form-search");
        var $filter_company = this.priv_textbox(
            "filter_company_dropdown",
            "Company",
            null,
            [
                {
                    text: "Clear",
                    click: function() {
                        $("#filter_company_dropdown").val("");
                        self.apply();
                    }
                }
            ]
        ).appendTo($filter_company_form);

        self.priv_elements = [$filter_company_form];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        var self = this;
        $.each(self.priv_elements, function(key, val) {
            $parent.append(val);
        });
        var $filter_company_dropdown = $("#filter_company_dropdown");
        $filter_company_dropdown.keyup(function() { self.apply(); });
        $($filter_company_dropdown).autocomplete({
            source: self.priv_companies,
            appendTo: $parent,
            change: function() { self.apply(); },
            close: function() { self.apply(); }
        });

        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the company name \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var result = false;
        var pattern = $("#filter_company_dropdown").val();
        if (undefined === pattern || 0 == pattern.length)
            return true;
        var patterns = pattern.split(/,\s*/);
        $.each(patterns, function(key, val) {
            if (0 != val.length && (new RegExp(val, "i")).test(value))
                return result = true;
        });
        return result;

    }
});


/**
 * \class ContractFilter
 * \brief Filter on the contract type.
 */
var ContractFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \property priv_contract_types
     * \brief Array containing all tested contract types.
     */
    priv_contract_types: [
        {name: "CDI", label: "success" },
        {name: "CDD", label: "warning" },
        {name: "Internship", label: "info" },
        {name: "Alternance", label: "info" }
    ],
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var $form = $("<form>").prop("role", "form");
        var contracts = new Array();
        $.each(self.priv_contract_types, function(key, val) {
            contracts.push(
                '<span class="label label-' + val.label + '">' + val.name + '</span>'
            );
        });
        $filter_contract_combobox = this.priv_select_from_array(
            "filter_contract_combobox", contracts, {
                multiple: true,
                width: "10em",
                text: "Contracts"
            }
        )
            .prop("title", "Contracts")
            .appendTo($form);
        priv_elements = [$form];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        var self = this;
        $parent.append(priv_elements[0]);
        var $select = priv_elements[0].find("select");
        $select.change(function() { self.apply(); });
        $select.selectpicker("selectAll");
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job contract type \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var self = this;
        var contracts = $("#filter_contract_combobox").val();
        if (null === contracts)
            return true; // no contracts = all contracts.

        var result = false;
        $.each(contracts, function(key, val) {
            if (value.match(val)) {
                result = true;
                return false; // no futher tests. Got candidate.
            }
        });

        if (!result) {
            /* The contract description may be complete gibberish. In this
             * case, we display it. */
            var gibberish = true;
            $.each(self.priv_contract_types, function(key, val) {
                if (value.match(val.name)) {
                    gibberish = false;
                    return false;
                }
            });
            if (gibberish)
                return true;
        }
        return result;
    }
});


/**
 * \class SalaryFilter
 * \brief Filter on the salary.
 */
var SalaryFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \property priv_salary_hashmap
     * \brief Hashmap cache containing salary range of computed offers.
     */
    priv_salary_hashmap: [],
    /**
     * \property priv_accept_na
     * \brief Filter the offers without any data on the salary.
     */
    priv_accept_na: true,
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \fn priv_range_from_string(salary_description)
     * \brief Extracts a salary range from a job description.
     *
     * \returns [\a min, \a max] : a two element array; \a min being the lowest salary
     * in kiloeuros (k€) and \a max the highest.
     */
    priv_range_from_string: function(salary_description)
    {
        var get_range = function(str) {
            var values = salary_description
                .replace(/[ ,.]?[0-9]{3}([,.]00)?/g, "")
                .replace(/([0-9]+) ?k€?/ig, "$1")
                .match(/[0-9]+/g);
            if (null == values)
                return [];
            switch (values.length)
            {
            case 0:
                return [];
            case 1:
                return [values[0], values[0]];
            case 2:
                if (values[0] > values[1])
                    return [values[1], values[0]];
                return values;
            default:
                return [
                    Math.min.apply(null, values),
                    Math.max.apply(null, values)
                ];
            }
        };
        if (null == this.priv_salary_hashmap[salary_description]) {
            this.priv_salary_hashmap[salary_description] = get_range(salary_description);
        }
        return this.priv_salary_hashmap[salary_description];
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var max = 0;
        var min = 0;
        $("#offers > tbody > tr > td." + classname).each(function() {
            var range = self.priv_range_from_string($(this).text());
            if (2 == range.length) {
                min = 0 == min ? range[0] : Math.min(min, range[0]);
                max = Math.max(max, range[1]);
            }
        });

        var $filter_salary_slider = $("<div>", {id: "filter_salary_root"});

        /*
         * <form>
         *   <div>
         *     <span>feedback</span>                    [ 0k€ ; 45k€ ]
         *     <span><label><input /><label></span>     NA [ ]
         *   </div>
         * </form>
         * <div />                                      SLIDER
         */
        var $filter_salary_from = $(
            '<form role="form">' +
                '<span id="filter_salary_feedback" />' +
                '<span id="filter_salary_na">' +
                    '<label>' +
                        '<input id="filter_salary_na_checkbox" type="checkbox" />' +
                        '&nbsp;&nbsp;NA' +
                    '</label>' +
                '</span>' +
                '<div id="filter_salary_spacer" />' +
            '</form>'
        );

        $filter_salary_from
            .find("#filter_salary_na_checkbox")
            .prop("checked", "checked")
            .click(function() {
                self.priv_accept_na = $(this).prop("checked");
                Config.set("filter_salary_na_checkbox", self.priv_accept_na);
                self.apply();
            });
        Config.get("filter_salary_na_checkbox", function(value) {
            self.priv_accept_na = "true" == value;
            $filter_salary_from
                .find("#filter_salary_na_checkbox")
                .prop("checked", self.priv_accept_na);
        });

        var slide_callback = function(event, ui) {
            var min = $filter_salary_slider.slider("values")[0];
            var max = $filter_salary_slider.slider("values")[1];
            $filter_salary_from
                .find("#filter_salary_feedback")
                .html("[<b>" + min + "</b>k€&nbsp;;&nbsp;<b>" + max + "</b>k€]");
        };
        var change_callback = function(event, ui) {
            slide_callback(event, ui);
            self.apply();
        };
        $filter_salary_slider.slider({
            animate: "fast",
            max: max,
            min: min,
            range: true,
            values: [min, max],
            create: change_callback,
            change: change_callback,
            slide: slide_callback
        });
        priv_elements = [$filter_salary_from, $filter_salary_slider];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        $.each(priv_elements, function(key, val) {
            $parent.append(val);
        });
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job salary \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var min = 0, max = 1;
        var range_slider = $("#filter_salary_root").slider("values");
        var range_row = this.priv_range_from_string(value);
        // NA
        if (0 == range_row.length)
            return this.priv_accept_na;
        // Values
        return (
            0 == range_row.length
            || null == range_slider[0]
            || range_row[min] <= range_slider[max]
            && range_row[max] >= range_slider[min]
        );
    }
});


/**
 * \class SourceFilter
 * \brief Filter on the offers source.
 */
var SourceFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var sources = [];
        $("#offers > tbody > tr > td." + self.classname()).each(function() {
            var source = $(this).text();
            if (-1 == $.inArray(source, sources))
                sources.push(source);
        });
        sources.sort();

        var $form = $("<form>").prop("role", "form");
        $filter_source_combobox = this.priv_select_from_array(
            "filter_source_combobox", sources, {
                multiple: true,
                liveSearch: true,
                width: "8em",
                text: "Sources"
            }
        ).appendTo($form);
        priv_elements = [$form];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        this._super(this);
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        var self = this;
        $parent.append(priv_elements[0]);
        var $select = priv_elements[0].find("select");
        $select.change(function() { self.apply(); });
        $select.selectpicker("selectAll");
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job offer source \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var contracts = $("#filter_source_combobox").val();
        if (null === contracts)
            return true;
        var result = false;
        $.each(contracts, function(key, val) {
            if (val == value) {
                result = true;
                return false;
            }
        });
        return result;
    }
});


/**
 * \class LocationFilter
 * \brief Filter on the offers location.
 */
var LocationFilter = AbstractFilter.extend({
    /**
     * \property priv_master_filter
     * \brief The filter's \ref MasterFilter.
     */
    priv_master_filter: null,
    /**
     * \property priv_elements
     * \brief Array for internal use.
     */
    priv_elements: [],
    /**
     * \fn priv_select_from_array(id, choices, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, choices, options)  {
        return this._super(id, choices, options);
    },
    /**
     * \property priv_store
     * \brief Persistant data manager.
     */
    priv_store: new Persist.Store("googlemaps_api_results"),
    /**
     * \priv_query_googlemap_api(loc1, loc2, success, failure)
     * \brief Queries the Google Maps API server for the distance between \a loc1
     *      and \a loc2.
     */
    priv_query_googlemap_api: function(loc1, loc2, success, failure)
    {
        var uri = 'https://maps.googleapis.com/maps/api/distancematrix/json';
        var args = '?origins=' + loc1 + '&destinations=' + loc2 + '&sensor=false';
        var url = uri + args;
        $.getJSON(url)
        .done(function(data) {
                var result = data.rows[0].elements[0].distance.value;
                if (null == result) {
                    var error = data.error_message;
                    failure(error);
                }
                success(result);
        })
        .fail(failure("unknown error"));
    },
    /**
     * \priv_distance(loc1, loc2, callback)
     * \brief Computes the distance in kilometers between \a loc1 and \a loc2.
     */
    priv_distance: function(loc1, loc2, callback)
    {
        var self = this;
        var loc1id = escape(loc1);
        var loc2id = escape(loc2);
        var distid = loc1id + '-' + loc2id;
        this.priv_store.get(distid, function(status, distance) {
        /* Case #1: distance not yes in cache */
            if (!status || null == distance) {
                self.priv_query_googlemap_api(loc1, loc2, function(distance) {
                    self.priv_store.set(distid, distance);
                    callback(distance);
                }, function(error) {
                    console.warn('Unable to query Google Maps API to get a'
                        + ' distance between "' + loc1 + '" and "' + loc2
                        + '".\nGoogle Maps API returned "' + error + '".'
                    );
                    callback(null);
                });
        /* Case #2: distance in cache */
            } else
                callback(distance);
        });
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        return;
        this._super(classname, master_filter);
        var self = this;
        /* input type text */
        var $filter_location_text = $("<input>", {
            id: "filter_location_text",
            type: "text",
        }).keypress(function(event) {
            if (13 == event.which)
                self.apply();
        }).focusout(function(event) {
                self.apply();
        });
        /* refresh button */
        var $filter_location_refresh = $("<input>", {
            type: "button",
            value: "Actualiser",
        }).click(function() {
            self.apply();
        });
        /* reset button */
        var $filter_location_reset = $("<input>", {
            type: "button",
            value: "Effacer",
        }).click(function() {
            $("#filter_location_text").val("");
            self.apply();
        });
        /* maxdist slider */
        var $filter_location_slider_box = $("<div>");
        var $filter_location_feedback = $("<div>", {id: "filter_location_feedback"})
            .appendTo($filter_location_slider_box);
        var $filter_location_slider = $("<div>", {id: "filter_location_slider"})
            .appendTo($filter_location_slider_box);

        var slider_on_change = function(distance)
        {
            slider_on_slide(distance);
            Config.set("filter_salary_range", distance);
            self.apply();
        }
        var slider_on_slide = function(distance)
        {
            $filter_location_feedback.html("Max : <b>" + distance/1000 + "</b>&nbsp;km");
        }
        
        $filter_location_slider.slider({
            animate: "fast",
            /* all in meters */
            max: 250000,
            min: 5000,
            step: 500,
            value: 30000,
            create: function(event, ui) {
                Config.get("filter_salary_range", function(value) {
                    $filter_location_slider.slider("value", value);
                }, function() {
                    slider_on_slide($filter_location_slider.slider("value"));
                });
            },
            change: function(event, ui) {
                slider_on_change($(this).slider("value"));
            },
            slide: function(event, ui) {
                slider_on_slide($(this).slider("value"));
            }
        });

        priv_elements = [
            $filter_location_slider_box,
            $filter_location_text,
            $filter_location_refresh,
            $filter_location_reset,
        ];
    },
    /**
     * \fn apply()
     * \brief Applies the filters, calling \ref MasterFilter.apply().
     */
    apply: function() {
        //this._super(this); FIXME LocationFilter: temporarly removed until improvment.
    },
    /**
     * \property classname()
     * \see \ref AbstractFilter.classname()
     */
    classname: function() { return this._super(); },
    /**
     * \fn attach($parent)
     * \brief Attaches the DOM elements the given \a $parent.
     */
    attach: function($parent) {
        return false; // FIXME LocationFilter: temporarly removed until improvment.
        var filter = this;
        $.each(priv_elements, function(key, val) {
            $parent.append(val);
        });
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job location \a value according to the GUI data.
     * \returns \c true.
     *
     * The search location is compared in distance with the row location \a value
     * and, if the computed distance is less than the maximum distance given by
     * the search radius (slider), the row is enqueued to be hidden.
     * 
     * Due to the asynchronous way the distance is computed, this function always
     * returns \c true. Though, when a job offer is considered too far, this
     * function manually hide the row.
     */
    test: function(value)  { // FIXME: precalcul all distances on refresh click
        return true; // FIXME LocationFilter: temporarly removed until improvment.
        var self = this;
        var max_distance = 35000;
        var location = $("#filter_location_text").val();
        if (null == location || 0 == location.length || 0 == value.length)
            return true;
        window.setTimeout(function() {
            self.priv_distance(value, location, function(distance) {
                if (null != distance && max_distance < distance)
                    $("#offers > tbody > tr > td.location").filter(function() {
                        return (new RegExp(value, "i")).test($(this).text());
                    }).closest("tr").hide(100);
            });
        }, 100);
        return true;
    }
});


/**
 * \class Config
 * \brief an API to save parameter accross uses.
 */
var Config = {
	/**
	 * \property priv_store
	 * \brief Storage API.
	 */
	priv_store: new Persist.Store("config"),
	/**
	 * \fn priv_encode(name)
	 * \brief Internal encoding of a configuration name.
	 */
	priv_encode: function(name) {
	    return escape(name);
    },
    
	/**
	 * \fn get(name, success, failure = null)
	 * \brief Read the configuration parameter \a name.
	 * \param[in] name (\c string) The parameter name
	 * \param[in] success (\c {function(value)}) The success callback
	 * \param[in] failure (\c {function()}) The failure callback
	 */
	get: function(name, success, failure) {
		if (undefined === failure)
			failure = null;
	    this.priv_store.get(this.priv_encode(name), function(status, value) {
            if (!status || null == value) {
                if (null != failure)
                    failure();
            } else
                success(value);
        });
    },
    /**
     * \fn set(name, value)
     * \brief Write the configuration parameter \a name.
     */
    set: function(name, value) {
	    this.priv_store.set(this.priv_encode(name), value);
    }
};

/*
 * ENTRY POINT
 */
$(document).ready(function() {
    /* Sort the table */
    $("#offers").tablesorter({sortList: [[0,1]]});

    /* Insert the filters */
    var master_filter = new MasterFilter();
});
