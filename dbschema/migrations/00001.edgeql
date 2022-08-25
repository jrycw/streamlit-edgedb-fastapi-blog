CREATE MIGRATION m136l4vviwrm2lcnb7e6j7rksqa7yaswdse5vtrdj53xyojfpail2a
    ONTO initial
{
  CREATE ABSTRACT TYPE default::CreatedTimestamp {
      CREATE REQUIRED PROPERTY created_on -> std::datetime {
          SET default := (std::datetime_of_statement());
          SET readonly := true;
      };
  };
  CREATE ABSTRACT TYPE default::UpdatedTimestamp {
      CREATE REQUIRED PROPERTY updated_on -> std::datetime {
          SET default := (std::datetime_of_statement());
      };
  };
  CREATE ABSTRACT TYPE default::AutoTimeStamp EXTENDING default::CreatedTimestamp, default::UpdatedTimestamp;
  CREATE TYPE default::Post EXTENDING default::AutoTimeStamp {
      CREATE REQUIRED PROPERTY content -> std::str;
      CREATE REQUIRED PROPERTY title -> std::str {
          CREATE CONSTRAINT std::max_len_value(500);
          CREATE CONSTRAINT std::min_len_value(1);
      };
  };
  CREATE TYPE default::User EXTENDING default::AutoTimeStamp {
      CREATE REQUIRED PROPERTY email -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(100);
          CREATE CONSTRAINT std::min_len_value(1);
      };
  };
  ALTER TYPE default::Post {
      CREATE REQUIRED LINK author -> default::User {
          ON TARGET DELETE DELETE SOURCE;
      };
  };
  ALTER TYPE default::User {
      CREATE MULTI LINK posts := (.<author[IS default::Post]);
  };
};
