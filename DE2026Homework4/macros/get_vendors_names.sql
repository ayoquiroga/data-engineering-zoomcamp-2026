    {% macro get_vendors_names(vendor_id) -%}
    case {{ vendor_id }}
        when 1 then 'Creative Mobile Technologies, LLC.'
        when 2 then 'VeriFone Inc.'
        when 4 then 'Unknown Vendor'
        else 'Unknown'
    end
{%- endmacro %}