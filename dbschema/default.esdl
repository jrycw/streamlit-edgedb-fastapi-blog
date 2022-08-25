module default {
    abstract type CreatedTimestamp {
        required property created_on -> datetime {
            readonly := true;
            default := datetime_of_statement();
        }
    }

    abstract type UpdatedTimestamp{
        required property updated_on -> datetime {
            default := datetime_of_statement();
        }
    }

    abstract type AutoTimeStamp extending CreatedTimestamp, UpdatedTimestamp {}
    
    type User extending AutoTimeStamp {
        required property name -> str {
            constraint exclusive;
            constraint min_len_value(1);
            constraint max_len_value(100)
        };
        required property email -> str {
            constraint exclusive;
        };
        multi link posts := .<author[is Post] 
    }

    type Post extending AutoTimeStamp {
        required property title -> str {
            constraint min_len_value(1);
            constraint max_len_value(500)
        };
        required property content -> str;
        required link author -> User {
            on target delete delete source;
        }
    }
}