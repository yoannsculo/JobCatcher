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
    priv_rows_per_page: 10,
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
    priv_apply_on_row: function(row, source = null) {
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
    priv_show_page: function(page, source = null) {
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
        new TypeFilter("type", this).attach(
            $("#lineFilters > .type")
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
            $("<p>").appendTo("body")
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
    apply: function(source = null) {
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
    /**
     * \property priv_bar
     * \brief navigation bar as a jQuery object..
     */
    priv_bar: null,
    /**
     * \fn init(options = null)
     * \brief COnstructor.
     */
    init: function(options = null) {
        var self = this;
        this.priv_bar = $("<p>");
        this.priv_bar.pagination({
            pages: 1,
            displayedPages: 3,
            edges: 0,
            onPageClick: function(page) {
                options.change(page-1);
            }
        });
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
        this.priv_bar.pagination("setPagesCount", page_count);
    },
    /**
     * \fn acknoledge_page(page_number)
     * \brief Acknoledge the existance of page number \a page_number.
     *
     * Increase the total number of pages if necessary.
     */
    acknoledge_page: function(page_number) {
        var page_count = this.priv_bar.pagination("getPagesCount", page_count);
        if (page_number >= page_count)
            this.set_page_count(page_count+1);
    },
    /**
     * \fn set_page(page_number, silent = false)
     * \brief Set the current displayed page number.
     * \param[in] silent Either or not the callback bind to the "change page" event is to be called.
     */
    set_page: function(page_number, silent = false) {
        this.priv_bar.pagination("selectPage", page_number+1, silent);
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     */
    priv_select_from_array: function(id, options)  {
        var $result = $("<select>", {id: id});
        $.each(options, function(key, val) {
            var $elt = $("<option>");
            $elt.append(val);
            $result.append($elt);
        });
        return $result;
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
    apply: function(source = null) {
        if (null != this.priv_master_filter)
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var $filter_pubdate_combobox = this.priv_select_from_array(
            "filter_pubdate_pivot", ["Tout", "Avant", "Le", "Après"]
        );
        var $filter_pubdate_root = $("<input>", {id: "filter_pubdate_root"});
        priv_elements = [$filter_pubdate_combobox, $filter_pubdate_root];
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
        priv_elements[0].change(function() {
            filter.apply();
        });
        $("#filter_pubdate_root").datepicker({
	    autoSize: true,
	    buttonText: "Calendar",
	    buttonImage: "img/calendar-16.png",
	    dateFormat: "yy-mm-dd",
	    defaultDate: 0,
	    showOn: "button",
	    onSelect: function(date_text, sender) {
	        filter.apply();
	    }
        });
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the date \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        if ("" == $("#filter_pubdate_root").val())
            return true;
        var date_format = $("#filter_pubdate_root").datepicker("option", "dateFormat");
        var row_date = $.datepicker.parseDate(date_format, value);
        var pivot_date = $("#filter_pubdate_root").datepicker("getDate");
        var pivot_type = $("#filter_pubdate_pivot :selected").text();
        switch(pivot_type)
        {
        case "Tout":
            return true;
        case "Avant":
            return pivot_date >= row_date;
        case "Le":
            return Math.abs(pivot_date - row_date) < 1000*86400-1;
        case "Après":
            return pivot_date <= row_date;
        default:
            console.error("Inconsistancy here. Must match <select> creation on init().");
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var $filter_type_combobox = this.priv_select_from_array(
            "filter_type_pivot", ["Tout", "noSSII", "SSII"]
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
        case "Tout":
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        var $filter_title_text = $("<input>", {
            id: "filter_title_text",
            type: "text",
        });
        var $filter_title_reset = $("<input>", {
            type: "button",
            value: "Effacer",
        });
        $filter_title_text.keyup(function() {
            self.apply();
        });
        $filter_title_reset.click(function() {
            $("#filter_title_text").val("");
            self.apply();
        });
        priv_elements = [$filter_title_text, $filter_title_reset];
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
        if (0 == pattern.length)
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
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

        $filter_company_combobox = $("<input>", {
            id: "filter_company_combobox",
        });
        $filter_company_combobox.autocomplete({
            source: companies
        });
        var $filter_company_reset = $("<input>", {
            type: "button",
            value: "Effacer",
        }).click(function() {
            $filter_company_combobox.val("");
            self.apply();
        });
        this.priv_elements = [$filter_company_combobox, $filter_company_reset];
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
        var $filter_company_combobox = this.priv_elements[0];
        $filter_company_combobox.keyup(function() { self.apply(); });
        $($filter_company_combobox).autocomplete({
            appendTo: $parent,
            change: function() { self.apply(); },
            close: function() { self.apply(); }
        });
        $.each(self.priv_elements, function(key, val) {
            $parent.append(val);
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
        var pattern = $("#filter_company_combobox").val();
        if (0 == pattern.length)
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
    },
    /**
     * \fn init(classname, master_filter)
     * \brief Constructor.
     */
    init: function(classname, master_filter) {
        this._super(classname, master_filter);
        var self = this;
        $filter_contract_combobox = this.priv_select_from_array(
            "filter_contract_combobox", ["Tout", "CDI", "CDD", "Stage"]
        );
        priv_elements = [$filter_contract_combobox];
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
        priv_elements[0].change(function() {self.apply();});
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job contract type \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var contract = $("#filter_contract_combobox :selected").text();
        return "Tout" == contract || value == contract;
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
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
                .replace(/[ ,.]?[0-9]{3}(\.00)?/g, "")
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
        var $filter_salary_feedback = $("<span>", {id: "filter_salary_feedback"});
        var $filter_salary_na = $("<span>");

        var $filter_salary_na_label = $("<label>")
            .attr("for", "filter_salary_na_checkbox")
            .text("NA")
            .appendTo($filter_salary_na);
        var $filter_salary_na_checkbox = $("<input>", {
            id: "filter_salary_na_checkbox",
            type: "checkbox",
            checked: "checked"
        })
        .click(function() {
            self.priv_accept_na = $(this).prop("checked");
            Config.set("filter_salary_na_checkbox", self.priv_accept_na);
            self.apply();
        }).appendTo($filter_salary_na);
        Config.get("filter_salary_na_checkbox", function(value) {
            self.priv_accept_na = "true" == value;
            $filter_salary_na_checkbox.prop("checked", self.priv_accept_na);
        });

        var slide_callback = function(event, ui) {
            var min = $filter_salary_slider.slider("values")[0];
            var max = $filter_salary_slider.slider("values")[1];
            $filter_salary_feedback.html("De <b>" + min + "</b>k€ à <b>" + max + "</b>k€");
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
        priv_elements = [$filter_salary_feedback, $filter_salary_na, $filter_salary_slider];
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
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
        sources = (new Array("Tout")).concat(sources);

        $filter_source_combobox = this.priv_select_from_array(
            "filter_source_combobox", sources
        );
        priv_elements = [$filter_source_combobox];
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
        priv_elements[0].change(function() { self.apply(); });
        return true;
    },
    /**
     * \fn test(value)
     * \brief Tests the job offer source \a value according to the GUI data.
     * \returns Either \c true of \c false.
     */
    test: function(value)  {
        var source = $("#filter_source_combobox :selected").text();
        return "Tout" == source || value == source;
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
     * \fn priv_select_from_array(id, options)
     * \brief Creates detached <select> elements from the \a options array.
     * \see \ref AbstractFilter.priv_select_from_array(id, options)
     */
    priv_select_from_array: function(id, options)  {
        return this._super(id, options);
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
	get: function(name, success, failure = null) {
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
